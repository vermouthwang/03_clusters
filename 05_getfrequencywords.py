"""
6.1010 Spring '23 Lab 9: Autocomplete
"""

# NO ADDITIONAL IMPORTS!
import doctest
from text_tokenize import tokenize_sentences
import pickle


class PrefixTree:
    '''
    define a class for prefixtree
    '''
    def __init__(self):
        self.value = None
        self.children = {}
    
    def __findnode__(self, key):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError("given key is not a string")
        first = key[0]
        if first not in self.children:
            return []
        if len(key) == 1:
            return self.children[first]
        else:
            key = key[1:]
            return self.children[first].__findnode__(key)
        
    def __setitem__(self, key, value):
        """
        Add a key with the given value to the prefix tree,
        or reassign the associated value if it is already present.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError("given key is not a string")
        first = key[0]
        # calculate from the first node
        # if fist (single str) not in parent node's children dict
        # create new instance
        if first not in self.children:
            self.children[first] = PrefixTree()
        # if key is a single str (reach the last node)
        if len(key) == 1:
            self.children[first].value = value
        # if not last node, node value automactically none
        # go check next single str
        else:
            key = key[1:]
            # create new node instance and set value
            return self.children[first].__setitem__(key,value)

    def __changeitem__(self,key):
        if not isinstance(key,str):
            raise TypeError("given key is not a string")
        first = key[0]
        if first not in self.children:
            self.children[first] = PrefixTree()
        if len(key) == 1:
            if self.children[first].value is not None:
                self.children[first].value +=1
            else:
                self.children[first].value = 1
        else:
            key = key[1:]
            # create new node instance and set value
            return self.children[first].__changeitem__(key)

    def __getitem__(self, key):
        """
        Return the value for the specified prefix.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
    
        # return self.__getnode__(key).value
        if not isinstance(key,str):
            raise TypeError("given key is not a string")
        first = key[0]
        if first not in self.children:
            raise KeyError("key not exist")
        if len(key) == 1:
            return self.children[first].value
        else:
            key = key[1:]
            return self.children[first].__getitem__(key)

    def __delitem__(self, key):
        """
        (de-associate the value with the word)
        Delete the given key from the prefix tree(not delete it from the children)
        if it exists.
        Raise a KeyError if the given key is not in the prefix tree.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError("given key is not a string")
        first = key[0]
        # print(first)
        if first not in self.children:
            raise KeyError("key not exist")
        if len(key) == 1:
            if self.children[key].value is None:
                raise KeyError("key not exist")
            self.children[key].value = None
        else:
            key = key[1:]
            return self.children[first].__delitem__(key)

    def __contains__(self, key):
        """
        Is key a key in the prefix tree?  Return True or False.
        Raise a TypeError if the given key is not a string.
        """
        if not isinstance(key,str):
            raise TypeError("given key is not a string")
        try:
            return self.__getitem__(key) is not None
        except:
            return False

    def __iter__(self):
        """
        Generator of (key, value) pairs for all keys/values in this prefix tree
        and its children.  Must be a generator!
        """
        for single_str,next_node in self.children.items():
            current_key = single_str
            if next_node.children == {}:
                if self.__getitem__(current_key) is not None:
                    yield current_key,self.__getitem__(current_key)
            else:
                for i,j  in next_node.__iter__():   
                    yield current_key + i,j
                if self.__getitem__(current_key) is not None:
                    yield current_key,self.__getitem__(current_key)

def get_total(text):
    count = 0
    for sentence in tokenize_sentences(text):
        words = sentence.split()
        for word in words:
            count +=1
    return count


def word_frequencies(text):
    """
    Given a piece of text as a single string, create a prefix tree whose keys
    are the words in the text, and whose values are the number of times the
    associated word appears in the text.
    """
    tree = PrefixTree()
    for sentence in tokenize_sentences(text):
        words = sentence.split()
        for word in words:
            tree.__changeitem__(word)
    return tree
        

def autocomplete(tree, prefix, max_count=None):
    """
    Return the list of the most-frequently occurring elements that start with
    the given prefix.  Include only the top max_count elements if max_count is
    specified, otherwise return all.

    Raise a TypeError if the given prefix is not a string.
    """
    if not isinstance(prefix,str):
        raise TypeError("prefix is not a string")
    # recursionly find the prefix's tree
    if prefix == "":
        prefix_tree = tree
    else:
        prefix_tree = tree.__findnode__(prefix)
    if prefix_tree == []:
        return []

    # __iter__ find the most freqnet
    word_value_tuple = [ (v,k) for k,v in prefix_tree.__iter__()]
    if prefix != "" and tree.__getitem__(prefix) is not None:
        word_value_tuple.append((tree.__getitem__(prefix),prefix))
    
    word_value_tuple.sort()
    word_value_tuple.reverse()
    
    if max_count is None or len(word_value_tuple) < max_count:
        most_list = [prefix + words[1] if words[1]!= prefix 
                     else words[1] for words in word_value_tuple ]
    else:
        most_list=[prefix+word_value_tuple[i][1] 
                   if word_value_tuple[i][1] != prefix 
                   else prefix for i in range(max_count)]
    return most_list


def autocorrect(tree, prefix, max_count=None):
    """
    Return the list of the most-frequent words that start with prefix or that
    are valid words that differ from prefix by a small edit.  Include up to
    max_count elements from the autocompletion.  If autocompletion produces
    fewer than max_count elements, include the most-frequently-occurring valid
    edits of the given word as well, up to max_count total elements.
    """
    
    # get original prefix autocompeletion result
    compeletions = autocomplete(tree,prefix,max_count)
    # if enough suggestions
    if max_count is not None and len(compeletions) == max_count:
        return compeletions
    # if not engouh suggestions, generate valide single edits word
    #edit 1
    insertion_word = get_insertion_edited(prefix)
    #edit 2
    deletion_word = get_deletion_edited(prefix)
    #edit 3
    replacement_word = get_replacement_edited(prefix)
    #edit 4
    transpose_word = get_transpose_edited(prefix)
    all_edit = set(insertion_word+deletion_word+replacement_word+transpose_word)
    edit_word = []
    for words in all_edit:
        if tree.__contains__(words):
            edit_word.append(words)
    word_value_dict = {}
    for word in edit_word:
        word_value_dict[word] = tree.__getitem__(word)
    values = list(word_value_dict.values())
    values.sort()
    values.reverse()
    edited_list = []
    if max_count is not None:
        valid_edit_count = max_count - len(compeletions)
        for i in range(valid_edit_count):
            for key,value in word_value_dict.items():
                if value == values[i]:
                    if key not in compeletions:
                        edited_list.append(key)
        edited_result = edited_list[:valid_edit_count]                 
    else:
        edited_result = [keys for keys in edit_word if keys not in compeletions]
    return compeletions + edited_result

def get_insertion_edited(prefix):
    '''
    give a word prefix, add any one character in the range "a" to "z" 
    at any place in the word
    return a list of new word that is contained in the tree
    '''
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    result = []
    for char in alphabet:
        for i in range(len(prefix)+1):
            new_word = prefix[:i] + char +prefix[i:]
            result.append(new_word)
    return result

def get_deletion_edited(prefix):
    '''
    give a word prefix, remove any one character from the word 
    at any place in the word
    return a list of new word
    '''
    result = []
    for i in range(len(prefix)):
        new_word = prefix[:i] + prefix[i+1:]
        result.append(new_word)
    return result

def get_replacement_edited(prefix):
    '''
    give a word prefix, replace any one character in the word 
    with a character in the range a-z
    return a list of new word
    '''
    alphabet = "abcdefghijklmnopqrstuvwxyz"
    result = []
    for char in alphabet:
        for i in range(len(prefix)+1):
            new_word = prefix[:i] + char +prefix[i+1:]
            result.append(new_word)
    return result   

def get_transpose_edited(prefix):
    '''
    give a word prefix, remove any one character from the word 
    at any place in the word
    return a list of new word
    '''
    result = []
    for i in range(len(prefix)-1):
        new_word = prefix[:i] + prefix[i+1] + prefix[i] + prefix[i+2:]
        result.append(new_word)
    return result 

    
def word_filter(tree, pattern):
    """
    Return list of (word, freq) for all words in the given prefix tree that
    match pattern.  pattern is a string, interpreted as explained below:
         * matches any sequence of zero or more characters,
         ? matches any single character,
         otherwise char in pattern char must equal char in word.
    """
    # optimize pattern
    while "**" in pattern:
        pattern = pattern.replace("**","*")

    if pattern == "":
        if tree.value is None:
            return None         
        return [(pattern,tree.value)]
        
    if "?" not in pattern and "*" not in pattern:
        if tree.__contains__(pattern):
            return[(pattern,tree.__getitem__(pattern))]
        return None
    #if there is know char at the begining
    know = ""
    for char in pattern:
        if char not in ("?","*"):
            know += char
        else:
            break
    if know != "":
        try:
            tree = tree.__findnode__(know)
            if tree == []:
                return None
            pattern = pattern[len(know):]
        except:
            return None
    #recursion
    current_match = pattern[0]
    if current_match == "?":
        return match_questionmark(tree,pattern,know)
    elif current_match == "*":
        return match_star(tree,pattern,know)

    
def match_questionmark(tree,pattern,know):
    '''
    a helper function to match the current tree word with patten
    '''
    final_return = []
    if tree.children != {}:
        for next_char,next_node in tree.children.items():
            # print("?",pattern)
            recursion_match = word_filter(next_node,pattern[1:])
            if recursion_match is not None:
                # final_return += word_filter(next_node,pattern[1:]))
                for tuples in recursion_match:
                    if (know + next_char + tuples[0],tuples[1]) not in final_return:
                        final_return.append((know + next_char + 
                                             tuples[0],tuples[1]))
        if final_return == []:
            return None
        else:
            return final_return                
    # if no more node but pattern not end
    else:
        return None
def match_star(tree,pattern,know):
    '''
    a helper function to match the current tree word with patten
    '''
    final_return = []
    recursion_match_zero = word_filter(tree,pattern[1:])
    if recursion_match_zero is not None:
        # print("zero",pattern)
        for tuples in recursion_match_zero:
            if (know + tuples[0],tuples[1]) not in final_return:
                final_return.append((know + tuples[0],tuples[1]))
    for next_char, next_node in tree.children.items():    
        # match one
        recursion_match_one = word_filter(next_node,pattern[1:])
        if recursion_match_one is not None:
            for tuples in recursion_match_one:
                if (know + next_char + tuples[0],tuples[1]) not in final_return:
                    final_return.append((know + next_char + tuples[0],tuples[1]))
        # match more 
        recursion_match_more = word_filter(next_node,"?"+pattern)
        if recursion_match_more is not None:
            for tuples in recursion_match_more:
                if (know + next_char + tuples[0],tuples[1]) not in final_return:
                    final_return.append((know + next_char + tuples[0],tuples[1]))
    if final_return == []:
        return None
    else:
        return final_return        


# you can include test cases of your own in the block below.
if __name__ == "__main__":
    doctest.testmod()
    with open("philosophy_merge.txt", encoding="utf-8") as f:
        text = f.read()
    
    t = word_frequencies(text)
    # count  = 0
    # for i in t.__iter__():
    #     count+=1
    # print(count)
    freq_word = autocorrect(t,"",15000)
    validate_word = []
    for word in freq_word:
        if len(word) >= 3:
            validate_word.append(word)
    
    with open("philo_freq_15000.pickle", "wb") as f:  
        pickle.dump(validate_word, f)  
    
    # print("philosophy" in freq_word)
    
    

    # print(autocomplete(t,"gre",6))
    # print(autocorrect(t,"hear"))
    # t = PrefixTree()
    # t['man'] = ''
    # t['mat'] = 'object'
    # t['mattress'] = ()
    # t['map'] = 'pam'
    # t['me'] = 'you'
    # t['met'] = 'tem'
    # t['a'] = '?'
    # t['map'] = -1000
    # for i in t.__iter__():
    #     print(i)

    # t = from_dict(c)
    # print("ori_set:",set(t))


        # if current_match != "?" and current_match != "*":
    #     # next_tree = tree.__findnode__(current_match)
    #     if current_match in tree.children:
    #         next_tree = tree.children[current_match]
    #         final_return.append(word_filter(next_tree,pattern[1:]))
    # t = word_frequencies('case')
    # # # # # # print(t.__getitem__("mi"))
    # result = word_filter(t, '*?*?*')
    # print(result)
    # print(result)patterns = ('*ing', '*ing?', '****ing', '**ing**', '????', 'mon*',
    # "***dif**"


    
    # result = word_filter(w, patterns)
    # print("result",len(result))
    
    # diff = set(expected) - set(result)
    # diff= list(diff)
    # print("diff",diff[:20])


        # assert len(expected) == len(result), 'incorrect word_filter of %r' % i
        # assert set(expected) == set(result), 'incorrect word_filter of %r' % i
