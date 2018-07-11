from _context import dataknead
from dataknead import Knead
from itertools import chain

# Read json file
entity = Knead("input/entity.json")

# Write back to a json file, indented
entity.write("output/entity.json", indent = 4)

Knead("input/names.txt").write("output/names.json")

# Print the description using query()
print(entity.query(".entities.Q184843.descriptions.en.value"))

# Get all the sitelinks and show the three different ways we can write
# this to a csv file.
# First get the sitelinks as a list using 'apply'
sitelinks = entity.query(".entities.Q184843.sitelinks").apply(lambda d:list(d.values()))

# First write it as a list with dicts, adding a header
sitelinks.write("output/sitelinks-header.csv")

# Write as a single textfile, with just the titles
sitelinks.map(lambda d:d["title"]).write("output/sitelinks-single.txt")

# And wait, we can even do this:
sitelinks.map("title").write("output/sitelinks-single.txt")

# Then write it as a list with two columns, only containing site and title
# and manually added fieldnames
sitelinks.map(("site", "title")).write("output/sitelinks-twocol.csv")

# Note that this is the same thing as writing
sitelinks.map(lambda d:{"site" : d["site"], "title" : d["title"]}).write("output/sitelinks-twocol.csv")

# Let's also make a list of all titles that are not 'Blade Runner'
sitelinks.map("title").filter(lambda t:t != "Blade Runner").write("output/sitelinks-other-title.csv")

# Some loaders can also have additional loading options
Knead("output/sitelinks-header.csv", has_header = True).write("output/sitelinks-header.json", indent = 4)

# Here's a pretty complex example, showing off all the different methods
# First define two helper functions we are going to be using
def propvalue(claim):
    claim = Knead(claim)

    return {
        "id" : claim.query(".mainsnak.datavalue.value.id").data(),
        "property" : claim.query(".mainsnak.property").data()
    }

def transform(claims):
    values = chain.from_iterable(claims.values())
    return [propvalue(c) for c in list(values)]

# Finally, query claims, flatten them and write to csv
entity.query(".entities.Q184843.claims").apply(transform).write("output/claims.csv")
