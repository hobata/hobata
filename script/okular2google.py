# okular export txt to google translate
# -*- coding: utf-8 -*-

import os, sys, re, time

def print_help():
  print "This program needs one parameter."
  print "Usage:"
  print " python okular2google.py [filename]"
  print "Parameter:"
  print " filename: okular exported txt file"
  print "output to stdout\n"

# table cell match pattern
ptn_h = r"  [a-z0-9A-Z(]" # any char. except space
re_h = re.compile(ptn_h)

tbl_col = []
def chkConRow(mlist):
  global tbl_col
  if len(tbl_col) >= len(mlist):
    for m in mlist:
      if m in tbl_col:
        tbl_col = mlist
        return True # continue row
  tbl_col = mlist
  return False # new row

strDic = {}
def makeTableRaw(r):
  global strDic
  strRaw = ""
  mlist = []
  iter = re.finditer(re_h, r, flags=0)
  for m in iter:
    mlist.append(m.start())
  retCont = chkConRow(mlist)
  if retCont:
    for i, m in enumerate(mlist): # append string
      if m in strDic:
        if m <> mlist[-1]: # last item
          # a head of next
          strDic[m] = strDic[m] + " " + r[m+2:mlist[i+1]].strip()
        else:
          strDic[m] = strDic[m] + " " + r[m+2:] # tail
          strDic[m] = strDic[m].replace("\n", "")
  else:
    # print row
    for k, v in sorted(strDic.items()): # sort by key
      strRaw = strRaw + "\n" + v.strip()
    # new row
    strDic = {}
    for i, m in enumerate(mlist):
      if m == mlist[-1]: # last item
        strDic[m] = r[m+2:] # tail
        strDic[m] = strDic[m].replace("\n", "") # tail
      else:
        strDic[m] = r[m+2:mlist[i+1]].strip() # a head of next

  return len(mlist), retCont, strRaw

# MAIN
argvs = sys.argv  # list of command line
argc = len(argvs) # prameter number

if argc != 2:
  print_help()
  sys.exit()

if not os.path.exists(argvs[1]):
  print "no source file"
  sys.exit()

#open files
infile = open(argvs[1], "r")
read_lines = infile.readlines()
infile.close()

# store status area
lineStatus = [] # each line status
tableRaw = [""] * len(read_lines)
for i, r in enumerate(read_lines):
  if "..." in r:
    lineStatus.append("a") # table of contents
    continue
  if r[:2] == "  ": # may be table
    col, newRow, strRaw  = makeTableRaw(r)
    if strRaw <> "":
      tableRaw[i] = strRaw
    prev = read_lines[i-1][0]
    if (prev == "a" or prev == "n") and col == 1:
      lineStatus.append("a") # 1st line of table is not "t1"
      continue
    lineStatus.append("t%d " % (col) + str(newRow) ) # in table
    continue
  else:
    lineStatus.append("n") # normal line
  if len(r) < 70 or r[-2] == "." or r[-2] == ":":
    lineStatus[i] = "a" # no action
    continue

for i, s in enumerate(lineStatus):
  if not "t" in s:
    print s + ":" + read_lines[i].replace("\n", "")
  if not tableRaw[i] == "":
    print "t:" + tableRaw[i]
