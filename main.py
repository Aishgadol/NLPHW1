import os
from docx import Document

lines=[]
filenames_data={}
prot_type=""
directory = ".venv/TextFiles"
filenames=[f for f in os.listdir(directory) if f.endswith('.docx')]

def extract_filename_data():
    for i in range(len(filenames)):
        #knesset num could be 1 or 2 digits

        tokens=filenames[i].split("_")
        tokens[2]=tokens[2][:tokens[2].index('.')]
        if tokens[1] == "ptv":
            prot_type = "committee"
        elif tokens[1] == "ptm":
            prot_type = "plenary"
        else:
            raise ValueError("Unexpected Error, Dont know ",tokens[1])
        filenames_data[i]=(int(tokens[0]),prot_type,int(tokens[2]))

def check_underline(para):
    # check if the sentence is underlined
    # there is 3 ways - 1. in style.base_style.font.underline 2. style.font.underline
    if para.style is not None and ((para.style.base_style is not None and para.style.base_style.font.underline) or (
            para.style.font is not None and para.style.font.underline)):
        return True
    # 3. run.underline : we go through all the runs because the first one isn't necessarily enough
    elif para.runs:
        for run in para.runs:
            if run.underline:
                return True
    return False

def check_bold(para):
    # check if the sentence is boldd
    # there is 3 ways - 1. in style.base_style.font.bold 2. style.font.bold
    if para.style is not None and ((para.style.base_style is not None and para.style.base_style.font.bold) or (
            para.style.font is not None and para.style.font.bold)):
        return True
    # 3. run.bold : we go through all the runs because the first one isn't necessarily enough
    elif para.runs:
        for run in para.runs:
            if run.bold:
                return True
    return False
extract_filename_data()
# for m in filenames_data:
#     print(m," : ",filenames_data[m])

#for i in range(len(filenames)):
for i in range(20,28):
    doc=Document(os.path.join(directory,filenames[i]))
    protocol_name=filenames[i]
    knesset_number=filenames_data[i][0]
    protocol_type=filenames_data[i][1]
    protocol_number=filenames_data[i][2]
    #print(protocol_name,"  ,  ",knesset_number,"  ,  ",protocol_type,"  ,  ",protocol_number)

    for paragraph in doc.paragraphs:
        if(protocol_type=="committee"):
            if((not check_bold(paragraph)) and check_underline(paragraph) and paragraph.text.endswith(':')):
                print(paragraph.text.strip()[:-1])

        elif(protocol_type=="plenary"):
            continue

        else:
            print("go fk yerself")


# some_file=filenames[11]
# file_path=os.path.join(directory,some_file)
# doc=Document(file_path)
# print(f'contents of file named {some_file}: ')
#
#
# for paragraph in doc.paragraphs:
#     if(check_bold(paragraph) and paragraph.text.endswith(':')):
#         print(paragraph.text)
