Your README must include these fields, organized however you see fit:
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
Hint hint, you’re only allowed one breadboard



Overview
This project utiilizes an STM32 Nucleo F446RE development board to vary LED output using an external photoresistor. Testing through use of an internal DAC is also implemented. As ambient light decreases a red light will increase in brightness until it is fully saturated having covered roughly a third of the range of the photoresistor. A green and blue LED cover the second and third parts of the range respectively. As an additional stipulation, the project is devoid of polling and other blocking calls. All interaction is event and interrupt driven.

Sensor Characterization
As the photoresistor on hand did not have a datasheet available, part of this project was characterizing the photoresistor's behavior. This was done by creating ___ different light levels between pitch black and full daylight to test the photoresistor's output. This data is shown in table ___ with visuals stored _____. -> chose based upon experimental results
* From this information we learned the phptoresistor behaves linearly, and through the use of a voltage divider described in "Circuit Design," was appropriately scaled to fit the range of accepted ADC values on the STM32.
* From this information I learned the photoresistor behaves non-linearly. To address this, I fitted a __(probably quadratic)___ to the data. Through the use of a voltage divider described in "Circuit Design," was appropriately scaled to fit the range of accepted ADC values on the STM32. Afterwards, the fitted ____(probably quadratic)___ is inverted in software to acheive a linear behavior as ambient luminosity increases.

LED Design
The first design consideration was how to smoothly vary the brightness of each LED. This project uses PWM to do so, as increasing the rate at which a PWM duty cycle flickers the light makes it appear to the human eye as though the LED is getting brighter. To better distinguish where in the range the photoresistor is, three LEDs are used to cover the brightest, middling, and darkest ranges that the photoresistor covers. Given this seperation, 999 steps between 0% and 100% duty cycle was arbitrarily chosen as reasonable to smoothly transition. Visual inspection validates this number of steps as sufficient. As the ambient light gets darker the colors light up in red, green, then blue order to match the phrasing of RGB.
* To dynamically change the brightness of each LED, PWM was used on TIM3 with each LED getting a dedicated channel on the timer. An arbitrary 1000Hz timer frequency was decided. Knowing TIM3 resides on APB1, we know from the earlier clock configuration that the base clock speed is 90MHz. As we are using PWM, we also know the number of positions between 0% and 100% of the duty cycle is set by how large the ARR value is. In this case, 999 steps was arbitrarily deemed a smooth enough transition. Plugging those values into the timer formula means my PSC value needed to be 89 to resolve the previously mentioned values. The colors light up in red, green, blue order to match the phrasing of RGB.

ADC Notes
With the LED architecture decided, 
* As part of using no blocking, I decided to use interrupts to utilize my ADC. Of the options provided, I decided to use the interrupt that triggered whenever a regular conversion finished. The output for this interrupt exists in the register for EOC, with the enable for this option existing in EOCIE for interrupt enable. As the ADC is simply used for a passive sampler, there is no need to use an injected group for any injected conversions. Additionally, the ADC is started with HAL_ADC_Start_IT(&HADC1) to initialize it into interrupt mode, with the address of ADC1 which is what is reading the analog sensor. According to the data sheet, the total unadjusted error in ADC accuracy at a frequency of 30MHz is typically +-2, with a max of +-5. For the purposes of this project, this variation from truth is considered acceptable, and not worth correcting for (***Check that this is the right frequency used in project, and if not, either say "its close enough" or interpolate with other frequency inaccuracies***).

Circuit design
The final step was circuit design. 
* The goal of the circuit is to take the brightness information from the photoresistor and maximize resolution by creating a range that spans all ADC values. This is achieved by taking the experimentally derived photoresistor brightness response information described in "Photoresistor characterization" which gave a minimum of 0Ohms and a maximum of XOhms. I knew the STM32 was capable of outputting 5V and the ADC measured a maximum of 3.3V relative to ground. As such, I decided to use a voltage divider with R1 being XOhms and R2 being the photoresistor (see diagram or photo ***build diagram and take photo***). Through this method, the maximum value of the voltage through the ADC (connected from the center of the voltage divider to ground) is 3.3V.


DAC Notes
* Reviewing the DAC shows a DAC_OUT minimum of 0.2V and a DAC_OUT maximum of V_DDA-0.2V. This the DAC is not good for testing in the first 0.2 of either edge, so for all testing we only used voltage values inside the safe range.

ADC Callback
* The ADC callback is designed to read the value stored in the ADC register, use the value to determine where in the range and thus what LED region it should be setting, and then pass in the proper lighting instructions to all three LEDs. The specified ranges split the valid range ADC values into thirds by taking the maximum and minimum ADC values and splitting that into thirds.




Datasheets
Red LED: https://www.digikey.com/en/products/detail/kingbright/WP7113ID/754-1264-ND/1747663
Green LED: https://www.digikey.com/en/products/detail/kingbright/WP7113LGD/754-1265-ND/1747664
Blue LED: https://www.digikey.com/en/products/detail/w-rth-elektronik/151051BS04000/732-5015-ND/4490009
