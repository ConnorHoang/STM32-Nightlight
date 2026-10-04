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






LED Design
* To dynamically change the brightness of each LED, PWM was used on TIM3 with each LED getting a dedicated channel on the timer. An arbitrary 1000Hz timer frequency was decided. Knowing TIM3 resides on APB1, we know from the earlier clock configuration that the base clock speed is 90MHz. As we are using PWM, we also know the number of positions between 0% and 100% of the duty cycle is set by how large the ARR value is. In this case, 999 steps was arbitrarily deemed a smooth enough transition. Plugging those values into the timer formula means my PSC value needed to be 89 to resolve the previously mentioned values. 

ADC Notes
* As part of using no blocking, I decided to use interrupts to utilize my ADC. Of the options provided, I decided to use the interrupt that triggered whenever a regular conversion finished. The output for this interrupt exists in the register for EOC, with the enable for this option existing in EOCIE for interrupt enable. As the ADC is simply used for a passive sampler, there is no need to use an injected group for any injected conversions. Additionally, the ADC is started with HAL_ADC_Start_IT(&HADC1) to initialize it into interrupt mode, with the address of ADC1 which is what is reading the analog sensor.

Circuit design
* The goal of the circuit is to take the brightness information from the photoresistor and maximize resolution by creating a range that spans all ADC values. This is achieved by taking the experimentally derived photoresistor brightness response information described in "Photoresistor characterization" which gave a minimum of 0Ohms and a maximum of XOhms. I knew the STM32 was capable of outputting 5V and the ADC measured a maximum of 3.3V (***chack this value***) relative to ground. As such, I decided to use a voltage divider with R1 being XOhms and R2 being the photoresistor (see diagram or photo ***build diagram and take photo***). Through this method, the maximum value of the voltage through the ADC (connected from the center of the voltage divider to ground) is 3.3V.
