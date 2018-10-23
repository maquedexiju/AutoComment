中文版见 README_CN.md  
According to some rules, comments are generated automatically.  

## Basic Idea

**The first step is split:**  

We can split the comment into some standard components, and each standard components can actually be split again, and finally become a very simple rule.  
E.g:

* {sentence}: The complete sentence, the largest component, may include:
    * {shortComment}: The simplest statement used to express positive emotions
    * {buyIt}: Where to get our smart hardware
    * {favoriteFunction}: Describe your favorite features
    * {sorrow}: Some suggestions, sorry (of course, very fake)
    * {symbol}: the end of the sentence to express emotions punctuation
    * {face}: emoji expression

The {shortComment} can also be split apart, except for some idioms, which can be {adv} {good}, an *adverb* plus a *positive adjective*.

**The second step is to expand:**  

We expand on each of these components to keep refining every one of them.
E.g:

* {adv} can be expanded to: very, the most, extremely ...  
* {good} can be extended to: easy to use, simple, elegant ...  

**The third step is to arrange the combination:**  

That is randomly selected and collocated, with the first two steps of bedding, we can combine a lot of comments.  
We still take {adv} {good} for example:

As above, we have expanded the two thesaurus, after which we randomly select the contents of which can be combined into the following:  
Very easy to use, the most elegant, extremely simple...  


## Basic Use

After determining how many comments you need to generate, setting up `totalNumbers` in the config file completes the basic setup.  
After the program execution is completed, the generated comment will appear in the bottom of *comment.txt*.

## The Basic Expansion of Lexicons

You can expand the lexicons if you need.
{sentence} is the final component to be used in the program, all of your modification should be based on this.
In order to adapt to various situations, the specific design is as follows:

### The Most Simple Case

```
lexiconName = [
    'content1',
    'content2',
    ...
]
```

Description:  
lexiconName is lexicon name  
contentN is the contents of the lexicon, note that do not add a comma after the last element  

Example:

```
adv = [
   'very',
   'themost',
   'extremely'
]
```

### Quote Other Lexicons
The syntax for referencing another lexicon in a lexicon is simple:

```
{lexiconName}
```

The name of the thesaurus wrapped with braces.  
Example:

```
shortComment = [
    '{adv} {good}',
    'impressive',
    'highly recommended',
    '{adv} like'
]
```

### Note
To comment for your own, starting with `#`

```
# This is a line comment
shortComment = [# The pound sign precedes the thesaurus, followed by the pound sign
    'content1',
    'content2',
    ...
]
```

### If You Want to Use the Component More than Once
There are two cases when one component is used more than once in a sentence.

#### Hope that the Last One and the Previous One is Consistent   
A bit similar to the concept of "pronoun", as long as the name is kept the same.  
E.g:

```
shortComment = [
    '{face} {face} {face} {adv} {good}'
    ...
]
```

#### Hope the Last One is Different from the Previous One
In this case, you need to add a number after the name of the subsequent components to distinguish, for example

```
shortComment = [
    '{face} {face1} {face2} {adv} {good}'
    ...
]
```

## Advanced Extension of Lexicon

### Empty Component
For the sake of nature, some components may need to be populated as ** empty **, you need to use `'_'`, do not use`''`.
E.g:

```
symbol = [
    '_', # This is correct, the result will not display "_", but what does not show
    '', # This is wrong and will cause the build to fail
    '!',
    '!!',
    '. ',
]
```

### Custom Weight

In order to be more natural and achieve better results, the probability of different content in the component may be different, at this time can be resolved by custom weights.  
Grammar is as follows:

```
lexiconName = [
    ['content1.1', chance1],
    ['content1.2', chance2],
    ...
    'content2.1',
    'content2.2',
    ...
]
```

Description:  
Content1.N is the need to customize the weight of the content, chanceN that corresponds to the content of the weight (probability).  
content2.N is content that does not require custom weights, and they share equally undefined weight.

Example:

```
face = [
    ['_', 0.8], # expressionless 80%
    ['😀', 0.05], # This expression represents 5%
    '😁', # All the remaining emoticons share the remaining 15% probability
    '😄',
    '😆',
    '🙂',
    '😏',
    '😉',
    '😊',
    '🙂'
]
```

### Restrictions
We offer you the function to identify whether there is a constraint between components.  
A device such as a **rice cooker** in {device} can only be associated with a **kitchen** location in {placeInHome}, so a separate way to maintain this restriction is needed.

This will be more troublesome, there are three steps:   

* Add a property for each of the two related components
* Add a description of the relationship between the constraints
* Describe the relationship between the descriptive information recorded in the component library

#### Add a Property for Each of the Two Related Components

Grammar is as follows:

```
lexicon = {
    'conditions': {}, # Used to record the constraints, not to fill here
    'v': {
        'content1': property1,
        'content2': property2,
        'content3': property3,
        ...
    }
}
```

Note: one property can be attached to more than one content.  
E.g:

```
lexicon = {
    'conditions': {}, # Used to record the constraints, not to fill here
    'v': {
        'content1': property1,
        'content2': property1,
        'content3': property2,
        ...
    }
}
```

#### Add a Description of the Constraints
Assuming that the names of the two component libraries are lexicon1 and lexicon2 respectively, the description table created needs to be named lexicon1VSlexicon2.
The contents of the table are as follows:

```
lexicon1VSlexicon2 = [
    'property1_of_lexicon1': [the_list_of_lexicon2_properties, ...],
    'property2_of_lexicon1': [the_list_of_lexicon2_properties, ...],
    'property3_of_lexicon1': [the_list_of_lexicon2_properties, ...]
]
```

#### Describe the Relationship Between the Descriptive Table Information in the Component Library
Need to increase in the conditions section of lexicon1: `'lexicon2': 'lexicon1VSlexicon2'`  
At the same time in the conditions section lexicon2 increase: `'lexicon1': 'lexicon1VSlexicon2'`

#### Example

```
# The first component library
device = {
    'conditions': {
        'placeInHome': 'deviceVSPlaceInHome'
    },
    'v': {
        'Socket': 'p', # plugin
        'Power Statistics Socket': 'p',
        'Bulb': 'b', # bulb
        'Lantern': 'b',
        'A / C': 'c', # circumstance
        'Air purifier': 'c',
        'Fan': 'c',
        'Water purifier': 'k', # kitchen
        'Home Camera': 's', # Safe
        'Magnetism': 's'
    }
}

# The second component library
placeInHome = {
    'conditions': {
        'device': 'deviceVSPlaceInHome',
    },
    'v': {
        'Living Room': 'l',
        'Kitchen': 'k',
        'Bedroom': 'b',
        'Study': 's',
        'Upstairs': 'u',
        'Downstairs': 'd',
        'Bathroom': 'w'
    }
}

# Record the relationship between the table
deviceVSPlaceInHome = {
    'p': ['l', 'k', 'b', 's', 'u', 'd', 'w'],
    'b': ['l', 'k', 'b', 's', 'u', 'd', 'w'],
    'c': ['l', 'k', 'b', 's', 'u', 'd'],
    'k': ['k', 'u', 'd'],
    's': ['l', 'k', 'b', 's', 'u', 'd']
}

```

### Constraints with Weight
We still take {device} as an example, add the probabilities to the property and wrap the property and probabily in square brackets.  
Example:

```
device = {
     'conditions': {
         'placeInHome': 'deviceVSPlaceInHome',
         'purpose': 'deviceVSPurpose'
     },
     'v': {
         'Socket': ['p', 0.2], # plugin
         'Power Statistics Socket': ['p', 0.05],
         'Wall switch': ['p', 0.03],
         'Bulb': ['b', 0.15], # bulb
         'Lantern': 'b',
         'Ceiling light': 'b',
         'Strip': 'b',
         'A / C': 'c', # circumstance
         'Air purifier': 'c',
         'Fan': 'c',
         'Water purifier': 'k', # kitchen
         'Milk machine': 'k',
         'Bread machine': 'k',
         'Home Camera': 's', # Safe
         'Magnetism': 's'
     }
}
```

