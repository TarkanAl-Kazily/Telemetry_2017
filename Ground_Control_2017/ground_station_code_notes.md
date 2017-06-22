## display.py -- attempt to fix the inability to parse faster data streams
line 91: commented out code that handles delaying the program loop
         Uncomment and decrease the delay to .005

## utility.py -- attempt to fix the broken lat/long values
line 74: the section that parses the values
         use float(str_vec[i]) to cast the value to a float
         change '-1' to '-1.0'

line 10: the regex for data values - might fix the parsing/display problem
         regex = "(![A-Z0-9]{1}[: ][-.0-9]+;)"
         - so add parens


