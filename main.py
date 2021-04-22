import requests
from bs4 import BeautifulSoup
import os
import re
import urllib.request
import pandas as pd


def CreateDirectory(i, Heading):
    WorkDirPath = os.getcwd()
    WorkDirPath += '/DPGTwikiData'
    if (Heading == None):
        return None
    if (i <= 26):
        DirName = WorkDirPath + '/13_Tev_Data/' + Heading.replace(' ','_')
    if (i >= 27) and (i <= 35):
        DirName = WorkDirPath + '/8_Tev_Data/' + Heading.replace(' ','_')
    if (i >= 36) and (i <= 52):
        DirName = WorkDirPath + '/7_Tev_Data/' + Heading.replace(' ','_')
    if (i >= 53) and (i <= 61):
        DirName = WorkDirPath + '/Old_Results/900_Gev_Data/' + Heading.replace(' ','_')
    if (i >= 62):  
        DirName = WorkDirPath + '/Old_Results/7_Tev_Data/' + Heading.replace(' ','_')
    try:
       os.makedirs(DirName)
    except:
       print("File exists")
    return DirName
     

HomePageUrl = "https://twiki.cern.ch/twiki/bin/view/CMSPublic/DPGResultsTRK"
HomePageResponse = requests.get(HomePageUrl)
HomePageSoup =  BeautifulSoup(HomePageResponse.content, "html.parser")


AttachmentExceptions = []
EmptySections = []
print("################################################################")
print("################ STARTING SCRAPPING PROCESS ####################")
print("################################################################")

for i in range(1, 72):
    SectionTitle = HomePageSoup.find("span", id="twistyIdCMSPublicDPGResultsTRK{}hide".format(i)).parent.a.span.string
    if SectionTitle == None: continue #Some Sections do not have titles or have wierd span structure
    print(SectionTitle)
    print("##################################################")
    print("############ FOLLOWING LINKS FOUND!! #############")
    print("##################################################")
    DirectoryName = CreateDirectory(i, SectionTitle)
    if i <= 32:
        # i = 32 -> Until 'Approved Tracker Alignment results for 2012'
        SubSectionLinks = HomePageSoup.find("div", id="twistyIdCMSPublicDPGResultsTRK{}toggle".format(i)).find_all("a")
        for SubSectionLink in SubSectionLinks:
            SubSectionUrlTail = SubSectionLink.get("href")
            UrlHead = "https://twiki.cern.ch"
            #We do not need to add "https://twiki.cern.ch" for i > 32 since href already contains it
            AttachmentNames = []
            SubSectionUrl = UrlHead + SubSectionUrlTail
            SubSectionTitle = SubSectionUrl.split('/')[-1]
            print(SubSectionUrl)
            print('______________________________________________________________')
            SubSectionResponse = requests.get(SubSectionUrl)
            SubSectionSoup =  BeautifulSoup(SubSectionResponse.content, "html.parser")
            AttachmentSearchString = SubSectionUrl.split('/')[-1]
            AttachmentLinks = SubSectionSoup.find_all(href = re.compile('/pub/CMSPublic/{}/'.format(AttachmentSearchString)))
            #Record Sections without Attachments
            if len(AttachmentLinks) == 0:   
                EmptySections.append(SectionTitle)
                continue 
            for AttachmentLink in AttachmentLinks:
                AttachmentUrl = AttachmentLink.get("href")
                AttachmentName = AttachmentUrl.split('/')[-1]
                if AttachmentName not in AttachmentNames:
                    AttachmentNames.append(AttachmentName)
                    print(AttachmentName)
                    AttachmentLocalPath = DirectoryName + '/' + AttachmentName
                    try:
                        urllib.request.urlretrieve(AttachmentUrl, AttachmentLocalPath)
                    except Exception as e: 
                        ExceptionDictionary = {"sectionTitle": SectionTitle, "subSectionTitle": SubSectionTitle, "attachmentName": AttachmentName, "attachmentLink": AttachmentLink, "error": e}
                        AttachmentExceptions.append(ExceptionDictionary)
            print('______________________________________________________________')            
            print('\n')
        print('\n')         
    else:
        #From i = 33 (Approved results for APS12), it does not link to a subsection, it directly contains the attachments. 
        AllLinks = HomePageSoup.find("div", id="twistyIdCMSPublicDPGResultsTRK{}toggle".format(i)).find_all("a")
        if len(AllLinks) == 0: continue 
        AttachmentLinks = []
        AttachmentNames = []
        for ALink in AllLinks:
            ALinkUrl = ALink.get("href")
            TransferProtocolFlag = ALinkUrl[0:8]
            ExtensionFlag = ALinkUrl[-4:]
            ExtensionChoices = ['.pdf', '.png', '.jpg', '.eps', '.gif']
            if (TransferProtocolFlag == 'https://') and (ExtensionFlag in ExtensionChoices):
                AttachmentUrl = ALinkUrl
                AttachmentName = AttachmentUrl.split('/')[-1]
                if AttachmentName not in AttachmentNames:
                    AttachmentNames.append(AttachmentName)
                    print(AttachmentName)
                    AttachmentLocalPath = DirectoryName + '/' + AttachmentName
                    try:
                        urllib.request.urlretrieve(AttachmentUrl, AttachmentLocalPath)
                    except Exception as e: 
                        ExceptionDictionary = {"sectionTitle": SectionTitle, "subSectionTitle": SubSectionTitle, "attachmentName": AttachmentName, "attachmentLink": AttachmentLink, "error": e}
                        AttachmentExceptions.append(ExceptionDictionary)
        if len(AttachmentNames) == 0: 
            EmptySections.append(SectionTitle)
    print('______________________________________________________________')            
    print('\n')


print('\n')
print("################################################################")
print("############### SCRAPPING PROCESS HAS ENDED ####################")
print("################################################################")


print('\n')
print('FOLLWING EXCEPTIONS/ERRORS WERE FOUND')
AttachmentExceptionsDf = pd.DataFrame.from_dict(AttachmentExceptions)
print(AttachmentExceptionsDf)

print('\n')
print('FOLLWING SECTIONS HAD NO ATTACHMENTS OR HAD RETREIVAL BUGS')
for EmptySection in EmptySections:
    print(EmptySection)




EdgeCaseIndex = [7,11,13,18,19,71]
EdgeCaseSections = ['Approved Strip performance plots 2017', 'Approved Strip radiation plots 2017', 
'Approved Strip radiation plots 2019', 'Approved Pixel Operations results 2020', 
'Approved Pixel Operations results 2019', '2010 commissioning plots Strip Tracker'] 
#The links 3,4 and 5 have to obtained by manually clicking an image since they have different link 
#than the name of the Section title
EdgeCaseUrls = ['https://twiki.cern.ch/twiki/bin/view/CMS/StripsOfflinePlots2017',
'https://twiki.cern.ch/twiki/bin/view/CMSPublic/StripsRadiationPlots2017',
'https://twiki.cern.ch/twiki/bin/view/CMSPublic/StripRadiationFeb2019LaserDriverThresholdCurrents',
'https://twiki.cern.ch/twiki/bin/view/CMSPublic/PixelOperationsFeb2020DepletionVoltagesLeakageCurrents',
'https://twiki.cern.ch/twiki/bin/view/CMSPublic/PixelOperationsFeb2019DepletionVoltagesLeakageCurrents',
'https://twiki.cern.ch/twiki/bin/view/CMSPublic/StripTrackerCommissioningPlots2010']
#Start with i=1 since for 'Approved Strip performance plots 2017' there are Authentication Issues
for i in range(1,6):
    EdgeCaseSection = EdgeCaseSections[i]
    DirectoryName = CreateDirectory(EdgeCaseIndex[i], EdgeCaseSection)
    EdgeCaseUrl = EdgeCaseUrls[i]
    print('------------------------')
    print(EdgeCaseSections[i])
    print('------------------------')
    EdgeCaseResponse = requests.get(EdgeCaseUrl)
    EdgeCaseSoup =  BeautifulSoup(EdgeCaseResponse.content, "html.parser")
    AttachmentSearchString = EdgeCaseUrl.split('/')[-1]
    AttachmentLinks = EdgeCaseSoup.find_all(href = re.compile('/pub/CMSPublic/{}/'.format(AttachmentSearchString)))
    AttachmentUrls= []
    for AttachmentLink in AttachmentLinks:
        AttachmentUrl = AttachmentLink.get("href")
        if AttachmentUrl.split('/')[0] != 'https:':
            AttachmentUrl = 'https://twiki.cern.ch' + AttachmentUrl
        if AttachmentUrl not in AttachmentUrls:
            AttachmentUrls.append(AttachmentUrl)
            AttachmentName = AttachmentUrl.split('/')[-1]
            print(AttachmentName)
            AttachmentLocalPath = DirectoryName + '/' + AttachmentName
            try:
                urllib.request.urlretrieve(AttachmentUrl, AttachmentLocalPath)
            except Exception as e: 
                ExceptionDictionary = {"sectionTitle": SectionTitle, "subSectionTitle": SubSectionTitle, "attachmentName": AttachmentName, "attachmentLink": AttachmentLink, "error": e}
                AttachmentExceptions.append(ExceptionDictionary)


#--------------------------------------------------------------------
#Other Edge Cases
#--------------------------------------------------------------------

#########12: Approved Strip radiation plots 2018 - Empty
#####29: Approved Strip Performance plots - ONLY LINKS (Leave it out)
#####38: Strip SN - 2011 Data - 2 Images 
#########54: Operational Fraction of Strip and Pixel Tracker - Empty
#####59: Strip Timing Scan - 1 Image 
#####60: Strip Hit Efficiency - 1 Image 
#########63: Operational Fraction of Strip and Pixel Tracker - Empty
#64: Pixels: Readout Threshold - CMSDocs ? 


for i in range(1, 75):
    Heading = HomePageSoup.find("span", id="twistyIdCMSPublicDPGResultsTRK{}hide".format(i)).parent.a.span.string
    print(i, ": ",  Heading)
