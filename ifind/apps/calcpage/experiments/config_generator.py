__author__ = 'rose'
"""
This script generates the config files for page calculator experiments
config file looks like:
[experiment]
engine = govuk
key=
domain=
cutoff=
maxqueries = 50
stopfile = stopwords.txt
cache = True
query_type = biterm
doc_portion_perc = 100
doc_portion_count =
selection_type = position
rank_type = odds
crawl_file =
divs= wrapper
"""
import os, sys
import ConfigParser

#parts = ["all","main"]
portions = ['100','75','50','25']
rankings = ["ranked","position_ranked","position","default"]
max_queries = ['100','150','200']
engines = ["govuk","sitebing"]
bing_key = "" #have a file called personal_bin_key.txt in this directory which contains your bing key
#todo domain should be appropriate e.g. gov.uk or  gla.ac.uk
domain = "gla.ac.uk"
#hard coded in stopfile location
stopfile= "/Users/rose/code/ifind/ifind/apps/calcpage/experiments/stopwords.txt"
rank_type = "odds"
top_path="results"
#hard coded in crawl file location,  need a different crawl file
crawl_file="/Users/rose/code/ifind/ifind/apps/calcpage/experiments/background.txt"
#DIVS SHOULD BE WRAPPER FOR GOV.UK AND MAINPAGE FOR GLA.AC.UK
divs = "mainpage"
config = ConfigParser.ConfigParser()
# set a number of parameters

def set_config():
    bing_key = read_bing_key()
    config.add_section("experiment")

    for portion in portions:
        for rank in rankings:
            for max_query in max_queries:
                for engine in engines:
                    directory = top_path + "/" + portion + "/" + rank + "/" + max_query + "/configs/"
                    #print directory
                    #if not os.path.exists(directory):
                    #    os.makedirs(directory)
                    if engine == 'sitebing' or engine == 'bing':
                        config.set("experiment","key",bing_key)
                    config.set("experiment", "engine",engine)
                    if engine == 'sitebing':
                        config.set("experiment","domain",domain)
                    config.set("experiment","maxqueries",max_query)
                    config.set("experiment","stopfile",stopfile)
                    config.set("experiment","query_type","biterm")
                    config.set("experiment","doc_portion_perc", portion)
                    config.set("experiment","selection_type",rank)
                    if rank == "ranked" or rank == "position_ranked":
                        config.set("experiment","rank_type",rank_type)
                        config.set("experiment","crawl_file",crawl_file)
                    if rank == "position_ranked" or rank == "position":
                        config.set("experiment","divs",divs)
                        #config.write(sys.stdout)
                    if not os.path.exists(directory):
                        os.makedirs(directory)
                    directory += "experiment_"+engine+".ini"
                    with open(directory, "w") as config_file:
                        config.write(config_file)
                    reset()


def reset():
    """
    to clear the config of values which aren't always set such as rank type crawl file and key
    :return:
    """
    config.remove_option("experiment","key")
    config.remove_option("experiment","domain")
    config.remove_option("experiment","rank_type")
    config.remove_option("experiment","crawl_file")
    config.remove_option("experiment","divs")

def read_bing_key():
    """
    a method to read in a bing API key from a text file
    :return: the key
    """
    with open("personal_bing_key.txt", "r") as f:
        key = f.read()
    return key


set_config()
print "config directories and files generated"
