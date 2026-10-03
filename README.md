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
