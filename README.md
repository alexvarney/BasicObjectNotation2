# BasicObjectNotation2

This project is a spiritual successor to a much simpler structured data format that I wrote previously. 
It has a JSON-like syntax (hence the name), and fully supports nested-value structures. 
This project is currently in an 'alpha'-quality state.

BasicObjectNotation looks like this:
    {
        example_key: "example_value";
        list: [1, 2, 3];
        object: {
          sub_value: "hello, world";
        };
    }

##Types

BON supports the following types, represented by the type in brackets:
    
    string (str)
    
    number (float, int)
    
    bon_list (list)
    
    bon_node (BONNode)
    
    bon_object (BONObject)
    
##Syntax

###String
Strings are enclosed in either single or double quotes.

    "string"
or

    'string'
    
###Number
Numbers can be interpreted as floats or integers in BON. They are written as a literal value. 
Numbers without a decimal or exponential value are automatically treated as integers. Exponential values, numbers with 
decimals, and integers with the character 'f' appended to them are interpreted as floats.

####Example Integers
    
    1
    
    10
    
####Example Floats
    
    10.0
    
    5f
    
    6.67e-11
    
###List
Lists are written in the same syntax as Python lists, with values seperated by commas. 
All BON types are acceptable values in a list.

####Example Lists
    
    [1, 2, 3]
    
    ["string1", "string2"]
    
    [1, 2e-5, 3.5, 4f, "5", {key: "value";} ];
    
###BONNode
A BONNode is a key value pair that accepts a string key and any BON type for a value. BONNode keys are defined without quotes
and must not begin with a number. BONNodes end with a semicolon.

####Example BONNodes

    key: "value";
    
    list: [1, 2, 3];
    
    object: {
      sub_value: "hello, world";
    };
    
###BONObject 
A BONObject is similar to a dict and contains BONNodes. 
BONObjects are enclosed within braces ('{}') and are not formatting sensitive.

####Example BONObject

    {
        example_key: "example_value";
        list: [1, 2, 3];
        object: {
          sub_value: "hello, world";
        };
    }
    
This can also be written as:

    {example_key: "example_value"; list: [1, 2, 3]; object: {sub_value: "hello, world"; }; }
