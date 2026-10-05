<!--Your README must include these fields, organized however you see fit:
● Overview: what it does, your breadboard prototype, and your demo video
● Circuit diagram: a schematic, your component values, and the calculations behind them
● Sensor characterization: your data, your plot, and what the relationship tells you
● System architecture: a diagram as well as an explanation of how data flows from the
timer through the ADC to the LEDs, plus the event-driven structure

Timer (outputs every RCC) -> ADC

● Design decisions: your constants, such as: sampling rate, PWM frequency, ADC
sampling time, and LED color order
● Register trace: for each ADC and timer setting you configured in CubeMX, name the
register and bit field it sets, cite the RM0390 section, and explain the value. Reading
HAL source to find these is OK, but verify against the reference manual. You may have
this as a link to another .md file from your README.md
● Testing: your self-test results and any other tests you ran, with data
● Obstacles: we’re expecting you to point out one major obstacle and how you solved it.
-->


## Overview
This project utiilizes an STM32 Nucleo F446RE development board to vary LED output using an external photoresistor. Testing through use of an internal DAC is also implemented. As ambient light decreases a red light will increase in brightness until it is fully saturated having covered roughly a third of the range of the photoresistor. A green and blue LED cover the second and third parts of the range respectively. As an additional stipulation, the project is devoid of polling and other blocking calls. All interaction is event and interrupt driven.

## System Overview <!--//////-->
System diagram available in 'media' folder.
| Peripheral | Register | Base Address | Offset | Relevant Bit(s) | Value | RM0390 Section | Explanation |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| ADC1 | `ADC_CCR` | `0x40012304` | `+0x04` | `ADCPRE[1:0]` (Bits 17:16) | `0b01` | Sec. 13.13.18 (p. 394) | Divides `PCLK2` (90 MHz) by 4 to run the ADC clock at 22.5 MHz. |
| ADC1 | `ADC1_CR1` | `0x40012004` | `+0x04` | `EOCIE` (Bit 5) | `1` | Sec. 13.13.2 (p. 383) | Enables interrupt generation when the End of Conversion (`EOC`) flag is set. |
| ADC1 | `ADC1_CR2` | `0x40012008` | `+0x08` | `EXTEN[1:0]` (Bits 29:28) | `0b01` | Sec. 13.13.3 (p. 384) | Enables hardware trigger detection on the rising edge of the timer trigger. |
| ADC1 | `ADC1_CR2` | `0x40012008` | `+0x08` | `EXTSEL[3:0]` (Bits 27:24) | `0b0110` | Sec. 13.13.3 (p. 384) | Selects `TIM2_TRGO` event to trigger regular channel conversions. |
| ADC1 | `ADC1_CR2` | `0x40012008` | `+0x08` | `EOCS` (Bit 10) | `1` | Sec. 13.13.3 (p. 385) | Sets `EOC` bit in `ADC1_SR` at the end of each individual regular conversion. |
| ADC1 | `ADC1_CR2` | `0x40012008` | `+0x08` | `CONT` (Bit 1) | `0` | Sec. 13.13.3 (p. 385) | Single conversion mode; ADC waits for each 100 Hz `TIM2_TRGO` pulse. |
| ADC1 | `ADC1_CR2` | `0x40012008` | `+0x08` | `ADON` (Bit 0) | `1` | Sec. 13.13.3 (p. 385) | Powers on and enables the ADC1 peripheral. |
| ADC1 | `ADC1_SMPR2` | `0x40012010` | `+0x10` | `SMP1[2:0]` (Bits 5:3) | `0b000` | Sec. 13.13.5 (p. 387) | Samples Channel 1 (`PA1`) for 3 ADCCLK cycles before conversion. |
| ADC1 | `ADC1_SQR1` | `0x4001202C` | `+0x2C` | `L[3:0]` (Bits 23:20) | `0b0000` | Sec. 13.13.9 (p. 389) | Defines a regular channel sequence length of 1 conversion. |
| ADC1 | `ADC1_SQR3` | `0x40012034` | `+0x34` | `SQ1[4:0]` (Bits 4:0) | `1` (`0b00001`) | Sec. 13.13.11 (p. 390) | Assigns `ADC1_IN1` (`PA1`) as the 1st conversion in the regular sequence. |
| ADC1 | `ADC1_DR` | `0x4001204C` | `+0x4C` | `DATA[15:0]` (Bits 15:0) | N/A | Sec. 13.13.14 (p. 391) | Read-only runtime register holding the 12-bit conversion result (0–4095); reading it clears `EOC` in `ADC1_SR`. |
| TIM2 | `TIM2_CR1` | `0x40000000` | `+0x00` | `DIR` (Bit 4), `CMS[1:0]` (Bits 6:5) | `DIR = 0`, `CMS = 0b00` | Sec. 17.4.1 (p. 547) | Edge-aligned upcounting mode from `0` to `ARR`. |
| TIM2 | `TIM2_CR1` | `0x40000000` | `+0x00` | `CEN` (Bit 0) | `1` | Sec. 17.4.1 (p. 548) | Enables the TIM2 counter. |
| TIM2 | `TIM2_CR2` | `0x40000004` | `+0x04` | `MMS[2:0]` (Bits 6:4) | `0b010` | Sec. 17.4.2 (p. 550) | Sends a `TRGO` trigger pulse to `ADC1` every time a TIM2 Update Event occurs. |
| TIM2 | `TIM2_PSC` | `0x40000028` | `+0x28` | `PSC[15:0]` (Bits 15:0) | `8999` | Sec. 17.4.11 (p. 564) | Divides the 90 MHz APB1 timer clock by `8999 + 1 = 9000` to yield a 10 kHz counter clock. |
| TIM2 | `TIM2_ARR` | `0x4000002C` | `+0x2C` | `ARR[31:0]` (Bits 31:0) | `99` | Sec. 17.4.12 (p. 564) | Rolls over every `99 + 1 = 100` ticks (`10 kHz / 100 = 100 Hz` ADC trigger rate). |
| TIM3 | `TIM3_CR1` | `0x40000400` | `+0x00` | `CEN` (Bit 0) | `1` | Sec. 17.4.1 (p. 548) | Enables the TIM3 counter. |
| TIM3 | `TIM3_PSC` | `0x40000428` | `+0x28` | `PSC[15:0]` (Bits 15:0) | `89` | Sec. 17.4.11 (p. 564) | Divides the 90 MHz APB1 timer clock by `89 + 1 = 90` to yield a 1 MHz counter clock. |
| TIM3 | `TIM3_ARR` | `0x4000042C` | `+0x2C` | `ARR[15:0]` (Bits 15:0) | `999` | Sec. 17.4.12 (p. 564) | Rolls over every `999 + 1 = 1000` ticks (`1 MHz / 1000 = 1 kHz` PWM frequency with 1000 steps). |
| TIM3 | `TIM3_CCMR1` | `0x40000418` | `+0x18` | `OC1M[2:0]` (Bits 6:4), `OC2M[2:0]` (Bits 14:12) | `0b110` | Sec. 17.4.7 (p. 557) | Sets Channels 1 and 2 to PWM Mode 1 (output HIGH while `CNT < CCRx`). |
| TIM3 | `TIM3_CCMR2` | `0x4000041C` | `+0x1C` | `OC3M[2:0]` (Bits 6:4) | `0b110` | Sec. 17.4.8 (p. 560) | Sets Channel 3 to PWM Mode 1 (output HIGH while `CNT < CCR3`). |
| TIM3 | `TIM3_CCER` | `0x40000420` | `+0x20` | `CC1E/2E/3E` (Bits 0, 4, 8), `CC1P/2P/3P` (Bits 1, 5, 9) | `CCxE = 1`, `CCxP = 0` | Sec. 17.4.9 (p. 561) | Enables PWM output on pins `PA6`, `PA7`, and `PB0` and sets active polarity HIGH. |
| TIM3 | `TIM3_CCR1` | `0x40000434` | `+0x34` | `CCR1[15:0]` (Bits 15:0) | `0`–`999` | Sec. 17.4.13 (p. 564) | Sets the active PWM duty cycle threshold for Channel 1 (Red LED on `PA6`). |
| TIM3 | `TIM3_CCR2` | `0x40000438` | `+0x38` | `CCR2[15:0]` (Bits 15:0) | `0`–`999` | Sec. 17.4.14 (p. 565) | Sets the active PWM duty cycle threshold for Channel 2 (Green LED on `PA7`). |
| TIM3 | `TIM3_CCR3` | `0x4000043C` | `+0x3C` | `CCR3[15:0]` (Bits 15:0) | `0`–`999` | Sec. 17.4.15 (p. 565) | Sets the active PWM duty cycle threshold for Channel 3 (Blue LED on `PB0`). |

## Circuit design
The First step was circuit design. The goal of the circuit is to take the brightness information from the photoresistor and maximize resolution by creating a range that spans all ADC values. This is achieved by taking the experimentally derived photoresistor brightness response information described in "Photoresistor characterization" which gave a minimum of 0Ohms and a maximum of XOhms. I knew the STM32 was capable of outputting 3.3V and the ADC measured a maximum of 3.3V relative to ground. As such, I decided to use a voltage divider with R1 being 5 KOhms and R2 being the photoresistor. as the voltage divider had better resolution when the resistors had similar values, allowing for more resolution at the brighter light levels. <!-- (see diagram or photo ***build diagram and take photo***). Through this method, the maximum value of the voltage through the ADC (connected from the center of the voltage divider to ground) is 3.3V. -->

## Sensor Characterization
As the photoresistor on hand did not have a datasheet available, part of this project was characterizing the photoresistor's behavior. As no luminosity sensor was available, two methods were tried to determine ranges of operation. The first involved taking a phone light and testing 8 values at 2 inch increments. From 14 inches to 0 inches the corresponding resistance values were: 3.7 kOhms, 2.9 kOhms, 2.2 kOhms, 1.6 kOhms, 1.1 kOhms, 700 Ohms, 400 Ohms, 0 Ohms<!--as shown in figure ____-->. Further qualitative measurements were taken at 6 different brightness levels between full daylight and pitch black that stepped between the absolutes by varying how closed a blind was. These measurements came out to 13.21 MOhms, 1.30 MOhms, 32.27 kOhms, 18.0 kOhms, 11.78 kOhms, 60 Ohms for full dark, fully closed blinds, mostly closed blinds, cloudy partial blinds, partial closed blinds, full daylight. Both quantitative and qualitative experimental results demonstrate non-linearity. As the quantitative measurements align reasonably well into a negative, linear fit with a logarithmic scale, and the qualitative results were non-linear in a similar trend, it is decided that the logarithmic extrapolation is a reasonable relationship across the entire photoresistor range.
<!--This data is shown in table ___ with visuals stored _____. -> chose based upon experimental results
* From this information we learned the phptoresistor behaves linearly, and through the use of a voltage divider described in "Circuit Design," was appropriately scaled to fit the range of accepted ADC values on the STM32.
* From this information I learned the photoresistor behaves non-linearly. To address this, I fitted a __(probably quadratic)___ to the data. Through the use of a voltage divider described in "Circuit Design," was appropriately scaled to fit the range of accepted ADC values on the STM32. Afterwards, the fitted ____(probably quadratic)___ is inverted in software to acheive a linear behavior as ambient luminosity increases. -->

## LED Design
The first design consideration was how to smoothly vary the brightness of each LED. This project uses PWM to do so, as increasing the rate at which a PWM duty cycle flickers the light makes it appear to the human eye as though the LED is getting brighter. To better distinguish where in the range the photoresistor is, three LEDs are used to cover the brightest, middling, and darkest ranges that the photoresistor covers. Given this seperation, 999 steps between 0% and 100% duty cycle was arbitrarily chosen as reasonable to smoothly transition. Visual inspection validates this number of steps as sufficient. As the ambient light gets darker the colors light up in red, green, then blue order to match the phrasing of RGB.
PWM used TIM3 with each LED getting a dedicated channel on the timer. An arbitrary 1000Hz timer frequency was decided to be sufficient. Knowing TIM3 resides on APB1, we know from the earlier clock configuration that the base clock speed is 90MHz. As we are using PWM, we also know the number of positions between 0% and 100% of the duty cycle is set by how large the ARR value is. In this case, 999 steps was arbitrarily deemed a smooth enough transition. Plugging those values into the timer formula means my PSC value needed to be 89 to resolve the previously mentioned values.
The red, green, and blue LEDs used resistor values of 300Ohms, 300Ohms, and 1150Ohms respectively to achieve roughly even brightness. These values were determined by reviewing the operating ranges within each LED's datasheet and using Ohms law to determine appropriate currents given the known 3.3V. Those numbers were then rounded to values I could make using resistors I had on hand.

## ADC Notes
As part of using no blocking, I decided to use interrupts to utilize my ADC. Of the options provided, I decided to use the interrupt that triggered whenever a regular conversion finished. The output for this interrupt exists in the register for EOC, with the enable for this option existing in EOCIE for interrupt enable. As the ADC is simply used for a passive sampler, there is no need to use an injected group for any injected conversions. Additionally, the ADC is started with HAL_ADC_Start_IT(&HADC1) to initialize it into interrupt mode, with the address of ADC1 which is what is reading the analog sensor. According to the data sheet, the total unadjusted error in ADC accuracy at a frequency of 30MHz is typically +-2, with a max of +-5. For the purposes of this project, this variation from truth is considered acceptable, and not worth correcting for <!--(***Check that this is the right frequency used in project, and if not, either say "its close enough" or interpolate with other frequency inaccuracies***).-->

## DAC Notes
Reviewing the DAC shows a DAC_OUT minimum of 0.2V and a DAC_OUT maximum of V_DDA-0.2V. This the DAC is not good for testing in the first 0.2 of either edge, so for all testing we only used voltage values inside the safe range. For testing, within the ADC callback, is a line of software that increments 'dac_val' by 10. This way, as the ADC callback occurred at a repeated frequency, the 'dac_val' can be used to increase the output of the DAC to simulate the photoresistor being exposed to a darker environment. There is also a check to loop the 'dac_val' back to a minimum if it reaches the maximum value the ADC can handle.

## ADC Callback
The ADC callback is designed to read the value stored in the ADC register, use the value to determine where in the range and thus what LED region it should be setting, and then pass in the proper lighting instructions to all three LEDs. The specified ranges split the valid range ADC values into thirds by taking the maximum and minimum ADC values and splitting that into thirds.

## Challenge
One major obstacle faced during this development process was the selection of resistor to pair with the photoresistor in the voltage divider. While I initially assumed I could choose a somewhat arbitrary resistor and scale the values in software, I found that selecting a more reasonable R1 resistor value made the photoresistor readouts to the ADC much easier to handle. I presume this is due to a phenomenon where having too large of a resistor collapses the voltage variation from the voltage divider to much smaller increments as the R1 resistor is fully drowning out the photoresistor.

## Datasheets
Red LED: https://www.digikey.com/en/products/detail/kingbright/WP7113ID/754-1264-ND/1747663
Green LED: https://www.digikey.com/en/products/detail/kingbright/WP7113LGD/754-1265-ND/1747664
Blue LED: https://www.digikey.com/en/products/detail/w-rth-elektronik/151051BS04000/732-5015-ND/4490009


## Generative AI
AI was used in the synthesis (not content) of the table in the system overview section. It was also used in the review of code, assisting in syntax errors both when I was not well versed enough in an error message to properly determine the key error and after identifying my mistake, providing the proper syntax. AI was also sporadically used to check which document I should look at to answer a question, with specific instructions to not provide me the answer itself.
