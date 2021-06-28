import os, time, re



# WINDOWS C / C++ MAKEFILE GENERATOR
##############################################################################################
#   CONFIGURATION   #
SEARCH_DIR = "./"     #Start location of the code

EXTERNAL_FOLDERS = []
GLOBAL_HEADERS = []

# COMPILER SELECTION
C_COMPILER = "gcc"
C_FLAGS = ["-std=c99"]

CPP_COMPILER = "g++"
CPP_FLAGS = ["-std=c++17"]

#LINKER SELECTION
LINKER = "g++"

# FLAGS FOR BOTH LANGUAGES (and linker)  
COMMON_FLAGS = ["-ggdb"] # also used in linker


OUTPUT_DIR = "Build"
OUTPUT_NAME = "main"

##############################################################################################

#Finds the path to a header
def find_header_path(header, all_headers):
    for h in all_headers:
         if header.find(h[1]) != -1:
             return h[0] + "/" + h[1] 
    return 0


found_cpp  = []
found_c    = []
found_head = []
found_dir  = []
o_files    = []

#STEP[] FIND ALL FILES
print("----------------------------")
print("STEP[1] FIND ALL THE FILES  ")
print("----------------------------")
time.sleep(1)
for dir, dirname, files in os.walk(SEARCH_DIR):
    if dir.find(OUTPUT_DIR) != -1:
        continue
    dir = dir.replace("\\","/").replace(" ", "\ ")
    for file in files:
        
        if file.find(" ") != -1:
            print("----------------------------")
            print("ERROR! FILES CANNOT HAVE SPACES IN THE NAME")
            print("----------------------------")
            print("INCORRECT FILE: " + dir + "/" + file)
            exit()

        if file.find(".cpp") != -1 or file.find(".cc") != -1: 
            found_cpp.append( (dir,file) )
            print(file)
        elif file.find(".c") != -1:
            found_c.append( (dir, file) )
            print(file)
        elif file.find(".h") !=-1:
            found_head.append((dir, file))
            print(file)
        if dir not in found_dir:
            found_dir.append(dir)

#STEP[] Create makefile
print("--------------------------------")
print("  STEP[2] CREATE MAKEFILE       ")
print("--------------------------------")
time.sleep(1)
fmakefile = open("Makefile",mode="w",encoding='utf-8')
dmakefile = ""


#STEP[] CREATE MAKEFILE VARS 
print("--------------------------------")
print("  STEP[3] CREATE MAKEFILE VARS  ")
print("--------------------------------")
time.sleep(1)

#Compiler Options
dmakefile += "C_COMPILER := " + C_COMPILER
dmakefile += "\nCPP_COMPILER := " + CPP_COMPILER
dmakefile += "\nLINKER := " + LINKER

#Flags
dmakefile += "\nC_FLAGS := "
for flag in C_FLAGS:
    dmakefile += flag + "\\\n" 

dmakefile += "\nCPP_FLAGS := "
for flag in CPP_FLAGS:
    dmakefile += flag + "\\\n" 

dmakefile += "\nCOMMON_FLAGS := "
for flag in COMMON_FLAGS:
    dmakefile += flag + "\\\n" 

#GLOBAL_INCLUDE
dmakefile += "\nGLOBAL_INC := "
for header in GLOBAL_HEADERS:
    dmakefile += "-include " + header + "\\\n" 

#OUTPUT
dmakefile += "\nOUTPUT_DIR := " + OUTPUT_DIR
dmakefile += "\nOUTPUT_NAME := "+ OUTPUT_NAME

#INLCLUDE OPTIONS FOLDERS
dmakefile +="\n\nFOLDER_INCLUDE:= "
for dir in found_dir + EXTERNAL_FOLDERS:
    dmakefile += "-I " + dir + "\\\n"

#CPP
dmakefile += "\nCPP := "
for cpp in found_cpp:
    dmakefile += cpp[0] + "/" + cpp[1] + "\\\n"

#C
dmakefile += "\nC := "
for c in found_c:
    dmakefile += c[0] + "/" + c[1] + "\\\n"

#SOURCE_DIRS
dmakefile += "\nSRC_DIR := "
for dir in found_dir:
    dmakefile += dir + " "
    
dmakefile += "\n\n"

#O
dmakefile += "\nO := "
for o in found_c + found_cpp:
    o_files.append(  ("$(OUTPUT_DIR)/" + o[0]+ "/" +o[1]).replace(".cpp",".o").replace(".cc",".o").replace(".c",".o") )
    dmakefile +=  o_files[len(o_files)-1] + "\\\n"

print("--------------------------------")
print("  STEP[4] CREATE TARGETS        ")
print("--------------------------------")
time.sleep(1)

#all
dmakefile += "\nall: clean compile\n\n"

#clean
dmakefile += "\nclean:\n\
\techo \"------------------------------------\"\n\
\techo \" STEP[]: Cleaning Folder $(OUTPUT_DIR)     \"\n\
\techo \"------------------------------------\"\n\
\trm -rf $(OUTPUT_DIR)\n\
\tsleep 2\n\n"

#compile
dmakefile += "\n\ncompile: echo_compile mkdir $(O)\n\
\techo \"------------------------------------\"\n\
\techo \" STEP[]: LINKING INTO EXE           \"\n\
\techo \"------------------------------------\"\n\
\tsleep 2\n\
\t$(LINKER) $(O) $(COMMON_FLAGS) -o $(OUTPUT_DIR)/$(OUTPUT_NAME).exe\n"


#mkdir
dmakefile += "mkdir : \n\
\tfor dir in $(SRC_DIR); do mkdir -p $(OUTPUT_DIR)/$$dir; done\n\n"

#echos
dmakefile+= "echo_compile : \n\
\techo \"------------------------------------\"\n\
\techo \" STEP[]: COMPILING SOURCE FILES     \"\n\
\techo \"------------------------------------\"\n\
\tsleep 2\n\n"



#o files

for src in found_cpp + found_c:
    
    fsrc = open(src[0] +"/"+ src[1],"r",encoding="utf-8")
    dsrc = fsrc.read()
    fsrc.close()
    included_headers = re.findall("#include .*", dsrc)

    dmakefile += ("$(OUTPUT_DIR)/"+src[0] +"/"+ src[1]).replace(".cpp",".o").replace(".cc",".o").replace(".c",".o") + " : " + src[0] + "/" + src[1] + " "

    for included_h in included_headers:
        included_h = find_header_path(included_h.replace("#include","").replace("\"","").replace("<","").replace(">",""), found_head)

        if included_h != 0:
            dmakefile += included_h + " " 
    
    if src[1].find(".cpp") != -1:
        dmakefile += "\n\
\techo \"Compiling C++ source file:"+ src[1] +"\"\n\
\t$(CPP_COMPILER) $(CPP_FLAGS) $(COMMON_FLAGS) $(GLOBAL_INC) $(FOLDER_INCLUDE) -o $@ -c " + src[0] + "/" + src[1]

    elif src[1].find(".c"):
        dmakefile += "\n\
\techo \"Compiling C source file:"+ src[1] +"\"\n\
\t$(C_COMPILER) $(C_FLAGS) $(COMMON_FLAGS) $(GLOBAL_INC) $(FOLDER_INCLUDE) -o $@ -c " + src[0] + "/" + src[1]

    dmakefile += "\n\n"

# SILENT
dmakefile += "\n\n.SILENT:\n\n"

#STEP WRITE MAKEFILE
fmakefile.write(dmakefile)
fmakefile.close()




