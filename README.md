PyBCPPsalter
============

A python library for converting the BCP Psalter hosted online into something hopefully more usable.
It automatically caches all of the content, so you don't have to worry about hammering their website.

# Stand Alone

```
Usage: psalter.py <command>
Valid Commands:
  --bcp <psalms>  Print out the BCP translation for each specified psalm.
                  <psalms> is a space-delimited list of numbers 1-150, inclusive
  --bcp-dump      Print out the entire BCP Psalter
```

Just toss that sucker on a command line.
e.g.

```
$ psalter.py --bcp 23 117
Psalm 23
1 The LORD is my shepherd; *
I shall not be in want.
2 He makes me lie down in green pastures *
and leads me beside still waters.
3 He revives my soul *
and guides me along right pathways for his Name's sake.
4 Though I walk through the valley of the shadow of death, I shall fear no evil; *
for you are with me; your rod and your staff, they comfort me.
5 You spread a table before me in the presence of those who trouble me; *
you have anointed my head with oil, and my cup is running over.
6 Surely your goodness and mercy shall follow me all the days of my life, *
and I will dwell in the house of the LORD for ever.

Psalm 117
1 Praise the LORD, all you nations; *
laud him, all you peoples.
2 For his loving-kindness toward us is great, *
and the faithfulness of the LORD endures for ever. Hallelujah!
```

# As a Library

Pretty straight-forward. Create a psalter and ask for a psalm. Note that these are 1-indexed. Hopefully this _minimizes_ mental gymnastics.

```
>>>from psalter import Psalter
>>>psalter = Psalter()
>>>long = psalter.psalm(119)
>>>long
Psalm 119
>>>len(long)
176
>>>print psalter.psalm(133)
Psalm 133
1 Oh, how good and pleasant it is, *
when brethren live together in unity!
2 It is like fine oil upon the head *
that runs down upon the beard,
3 Upon the beard of Aaron, *
and runs down upon the collar of his robe.
4 It is like the dew of Hermon *
that falls upon the hills of Zion.
5 For there the LORD has ordained the blessing: *
life for evermore.
```

If you don't like the print formatting, you've got access to the individual parts to print it the way you want:

```
>>> yummy = psalter.psalm(136)
>>> for v in yummy.verses[24:26]:
...     print v.a + '<br> ' + v.b
...
Who gives food to all creatures,<br> for his mercy endures for ever.
Give thanks to the God of heaven,<br> for his mercy endures for ever.
```

**NB:** the individual verses are 0-indexed. Sorry it's a mess.
