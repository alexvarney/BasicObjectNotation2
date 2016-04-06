from queue import deque
from enum import Enum

class BONType(Enum):
    """
    Enumeration of the different Types understood in Basic Object Notation
    """
    string = 1
    number = 2
    bon_object = 3
    bon_list = 4
    bon_node = 5
    invalid = 6

class TextQueue(deque):
    """
    Queue-like object inheriting from Deque for fast iteration through text
    """
    def __init__(self, data:str = None):
        super().__init__()
        if isinstance(data, str):
            for char in data:
                self.push(char)

    def __str__(self):
        return "".join([x for x in self])

    def __iter__(self):
        for x in range(0, len(self)):
            yield self.peek(x)

    @property
    def is_empty(self) -> bool:
        """
        Checks if the collection is empty.
        :return:
        """
        return len(self) == 0

    def peek(self, index = 0) -> str:
        """
        Gets a value from the collection without removing it.
        :param index: Number of chars to peek ahead.
        :return: A character.
        """
        return self[len(self)-(1+ index)] if len(self) > index else None

    def push(self, char: str):
        """
        Adds a value to the collection.
        :param char: Single character to add.
        :return: None
        """
        self.appendleft(char)

class BONNode():
    def __init__(self, key, value):
        self.key, self.value = key, value

    def __str__(self):
        if isinstance(self.value, list):
            list_repr = "[{}]".format(", ".join(str(x) for x in self.value))
            return "{}: {};".format(self.key, list_repr)
        else:
            return "{}: {};".format(self.key, self.value)

    def __contains__(self, item):
        return self.key == item or self.value == item

class BONObject():

    def __init__(self, nodes:list = None):
        self.nodes = nodes[:]

    def add_node(self, node: BONNode):
        """
        Adds a BONNode to the object
        :param node: BONNode entry to add to the collection.
        :return: None
        """
        self.nodes.append(node)

    def __str__(self):
        base = '{{\n\t{}\n}}'

        values = []
        print_list = lambda x: "[{}]".format(", ".join(str(y) for y in x))


        for x in self.nodes:
            values.append(str(x))

        return base.format("\n\t".join(values))

    def __contains__(self, item):
        for node in self.nodes:
            if node.key == item:
                return True
        return False

    def __getitem__(self, item):
        for node in self.nodes:
            if node.key == item:
                return node.value

        raise KeyError(str(item))

    def __delitem__(self, key):
        index = None
        for loop_index, value in enumerate(self.nodes):
            if value.key == key:
               index = loop_index

        if not index:
            raise KeyError
        else:
            del self.nodes[index]

    def __iter__(self):
        for value in self.nodes:
            yield value

class BONParser():
    opening_map = {
        '{': BONType.bon_object,
        '[': BONType.bon_list,
        '"': BONType.string,
        '\'':BONType.string,
        ':': BONType.bon_node
    }
    invalid_chars = ('\t', '\n')

    integer_digits = ('0123456789')
    float_digits = ('0123456789.fe-')

    def __init__(self, data: str):
        replaced = data.replace('\n', '').replace('\t', '')

        self.text = TextQueue(replaced)
        self.base_object = BONObject

    def determine_type(self) -> BONType:
        """
        Determines the type of the upcoming value in the character queue.
        :return: BONType of the next value.
        """


        is_escaped = False
        alpha_found = False

        for char in self.text:
            if not is_escaped:
                #check if char is one of the keys in opening_map
                if char in self.opening_map:
                    return self.opening_map[char]

                #logic to distinguish between a BONNode key with numeric characters
                #and a BONType.number
                elif char.isalpha() and not alpha_found:
                    alpha_found = True
                elif char.isdigit() and not alpha_found:
                    return BONType.number

            is_escaped = (char == '\\' and not is_escaped)

        return BONType.invalid

    def parse_value(self):
        """
        Recursively parses the upcoming character queue
        :return: The parsed result of the next value
        """
        type = self.determine_type()

        type_map = {
            BONType.number: self.parse_number,
            BONType.string: self.parse_string,
            BONType.bon_node: self.parse_node,
            BONType.bon_list: self.parse_list,
            BONType.bon_object: self.parse_object
        }

        return type_map[type]()

    def parse_number(self, data: TextQueue = None):
        """
        Parses a number from the upcoming text
        :param data: TextQueue of the value to parse from (defaults to self.text otherwise)
        :return: The parsed number
        """

        data = self.text if data is None else data
        buffer = TextQueue()

        while not data.is_empty and (data.peek() in self.float_digits or data.peek() == ' '):
            buffer.push(data.pop())

        if all((x in self.integer_digits or x == ' ') for x in buffer):
            return int(str(buffer))

        return self.parse_float(str(buffer))

    def parse_float(self, data: str):
        """
        Parses a BONType.number to a float()."
        :param data: The BONType.number to parse
        :return: A float.
        """
        if data.count('f') > 1:
            raise Exception("Float token error: too many tokens present.")
        elif 'f' in data and data.rindex('f') != len(data)-1:
            rindex = data.index('f')
            raise Exception("Float token error: misplaced token.")
        else:
            return float(data.strip('f'))

    def parse_string(self, data: TextQueue = None) -> str:
        """
        Parses a string enclosed in '"' characters
        :param data: TextQueue of the value to parse from (defaults to self.text otherwise)
        :return: The parsed string.
        """
        data = self.text if data is None else data
        buffer = TextQueue()
        start_found = False
        is_escaped = False

        #Look for the beginning of the quote, after it is found, start adding the upcoming characters to a new buffer
        #return the new buffer once the ending quote is found
        while not data.is_empty:
            char = data.pop()
            if start_found and not is_escaped and (char == '"' or char == '\''):
                return str(buffer)
            elif start_found and not char in self.invalid_chars:
                if not char == '\\' or is_escaped:
                    buffer.push(char)
            elif char == '"' or char == '\'':
                start_found = True

            is_escaped = (char == '\\' and not is_escaped)

        raise Exception('Expected token \' " \' not found.')

    def parse_list(self, data: TextQueue = None) -> list:
        """
        Parses a list
        :param data: TextQueue of the value to parse from (defaults to self.text otherwise)
        :return: A python list
        """

        new_list = []
        start_found = False

        data = self.text if data is None else data

        #Find the beginning of the list, and once it's found,
        #call self.parse_value() to extract the sub entires from the list
        #return once the end token (']') is found
        while not data.is_empty:
            char = data.pop()

            if not start_found and char == '[':
                start_found = True

            if start_found:
                if char == ',' or char == '[':
                    new_list.append(self.parse_value())
                elif char == ']':
                    return new_list
                elif not char == ' ':
                    raise Exception('Malformed list provided')



    def parse_node(self, data: TextQueue = None) -> BONNode:
        """
        Parses the key and value of a BONNode
        :param data: TextQueue of the value to parse from (defaults to self.text otherwise)
        :return: The parsed BONNode
        """
        data = self.text if data is None else data
        buffer = TextQueue()
        key, value = None, None

        #Find the key, and then return self.parse_value() to extract the value
        while not data.is_empty:
            char = data.pop()
            if char == ':':
                key = str(buffer).strip().lstrip()
                value = self.parse_value()
            elif char == ';':
                return BONNode(key, value)
            elif not char == ' ' and key == None:
                buffer.push(char)

        raise Exception("Expected token ';' not found.")



    def parse_object(self, data: TextQueue = None) -> BONObject:
        """
        Parses a BONObject
        :param data: TextQueue of the value to parse from (defaults to self.text otherwise)
        :return: BONObject containing parsed BONNode objects
        """
        data = self.text if data is None else data
        nodes = []
        start_found = False

        #Once start of object is found, parse BONNodes until the end token ('}') is found
        while not data.is_empty:
            char = data.peek()
            if char == '{':
                start_found = True
                char = data.pop()
                if not self.determine_type() == BONType.bon_node:
                    raise 'Invalid type, expected BONNode.'
                nodes.append(self.parse_value())
            elif char == '}':
                char = data.pop()
                return BONObject(nodes)
            elif start_found and not char == ' ':
                if not self.determine_type() == BONType.bon_node:
                    raise 'Invalid type, expected BONNode.'
                nodes.append(self.parse_value())
            else:
                data.pop()

        if not start_found:
            raise Exception("Expected token '{' not found.")
        else:
            raise Exception("Expected token '}' not found")

if __name__ == '__main__':

    #Testing Code

    example = '{value: "data"; list: [1, 2e-5, 3.5, 4f, "5", {key: "value";} ]; nested_object: { hello: "world"; }; };'

    p1 = BONParser(example)

    print("Input (string): " + example)
    print("Output (BONObject):")
    result = p1.parse_value()
    print(result)
    print()

    print("result['value']")
    print('>>> '+result['value'])
    print()
    print("str(result['list'])")
    print('>>> '+ str(result['list']))
    print()
    print("result['nested_object']['hello']")
    print('>>> '+ result['nested_object']['hello'])
    print()
    print("All values:")
    print("\n".join(str(value) for value in result))

    t = BONParser('value_1: "value";')
    print(t.parse_value())