#  Import necessary libraries
import text2emotion as te
import sys, nltk, codecs, csv
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup


#  Download necessary latest libraries & models for text to emotions
nltk.download('punkt')
nltk.download('omw-1.4')


#  Declare default encoding
DEFAULT_ENCODING = "utf8"

#  Safe resumable parsing where we can start from a specific page as well as id if needed
STARTING_PAGE = 1
STARTING_ID = 128948
#STARTING_PAGE = 2
#STARTING_ID = 134921

#  Declare CSV headers and file name
FIELD_NAMES = ['Id', 'Title', 'Comment', 'Created Date', 'Created By', 'Happy', 'Angry', 'Surprise', 'Sad', 'Fear']
CSV_FILE_NAME = 't2e_final.csv'
TOTAL = 'Total'

#  Declare Pie Chart Title
CHART_TITLE = 'Sentiment Analysis for Public Comment'


##############################
#  Load CSV and Show result  #
##############################
def showPieChart(y):
    #  Create the graph structure
    fig, ax = plt.subplots(figsize=(6, 6))

    #  Generate the pie chart with necessary data and structure details with percentages
    patches, texts, pcts = ax.pie(y, labels=FIELD_NAMES[5:], autopct='%.1f%%', wedgeprops={'linewidth': 3.0, 'edgecolor': 'white'}, textprops={'size': 'x-large'}, startangle=90)

    #  Generate various colors for the slices
    for i, patch in enumerate(patches):
        texts[i].set_color(patch.get_facecolor())

    #  Set the information color and title
    plt.setp(pcts, color='white', fontweight='bold')
    ax.set_title(CHART_TITLE)

    #  Show the chart
    plt.tight_layout()            
    plt.show()


#######################
#  Write to CSV file  #
#######################
def writeToCSVFile(writer, created_by, happy, angry, surprise, sad, fear, id = '', title = '', comment = '', created_date = ''):
    writer.writerow(
        {FIELD_NAMES[0]: id,
        FIELD_NAMES[1]: title,
        FIELD_NAMES[2]: comment,
        FIELD_NAMES[3]: created_date,
        FIELD_NAMES[4]: created_by,
        FIELD_NAMES[5]: happy,
        FIELD_NAMES[6]: angry,
        FIELD_NAMES[7]: surprise,
        FIELD_NAMES[8]: sad,
        FIELD_NAMES[9]: fear}
    )    


#####################################
#  Parse HTML Page and Show result  #
#####################################
def parseHTMLAndShowResult():    
    try:
      #  Open CSV file in append mode
      with codecs.open(CSV_FILE_NAME, 'a', encoding = DEFAULT_ENCODING) as csvfile:

        #  Write CSV header and initialize necessary variables
        writer = csv.DictWriter(csvfile, dialect=csv.unix_dialect, fieldnames=FIELD_NAMES)
        writer.writeheader()
        happy = angry = surprise = sad = fear = 0.0

        #  Loop through every HTML page to extract data
        #  Safe resumable parsing where we can start from a specific page if needed
        for i in range(STARTING_PAGE, 3):
            filename = "data\VirginiaRegulatoryTownHallViewComments" + str(i) + ".html"
            print("Processing "+ filename + " ... ", end="")

            #  Read and parse the HTML page
            with codecs.open(filename, encoding = DEFAULT_ENCODING, errors ='replace') as fp:
                print("parsing ... ", end="")
                soup = BeautifulSoup(fp, 'html.parser')
                print("done.")

                #  Find all occurances of class="Cbox" which is the main div section for every comment
                for div_cbox in soup.find_all(class_="Cbox"):

                    #  Extract the id
                    id = div_cbox['id'][4:]

                    #  Safe resumable parsing where we can start from a specific id if needed
                    if int(id) >= STARTING_ID:

                        #  Extract the comment which can come in various flavor (i.e. bullet points, images etc.)
                        print("Extracting comment " + id + " information ... ", end="")                    
                        title = div_cbox.find_all("strong")[1].get_text()
                        comment = div_cbox.find(class_="divComment")

                        #  If comment has a paragraph tag
                        if comment.p != None:
                           #  If comment paragraph has an image tag
                           if comment.p.img != None:
                              comment = title
                           else:
                              comment = comment.p.contents[0].get_text().replace('\r','').replace('\n','')
                        #  If comment has ordered list tag
                        elif comment.ol != None:
                           cmt = ""
                           idx = 1
                           #  Extract and save all list items as comment
                           for li in comment.ol.find_all("li"):
                               cmt += str(idx) + ". " + li.contents[0].get_text().replace('\r','').replace('\n','')
                               idx += 1
                           comment = cmt
                        #  Else use the title as comment
                        else:
                           comment = title

                        #  Extract the date
                        created_date = div_cbox.div.div.contents[0].get_text()

                        #  Extract the writer's information
                        created_by = div_cbox.strong.next_sibling.get_text().strip()

                        #  Predict the emotions from the comment
                        print("getting emotions ... ", end="")
                        data = te.get_emotion(comment)
                        writeToCSVFile(writer, created_by, data['Happy'], data['Angry'], data['Surprise'], data['Sad'], data['Fear'], id, title, comment, created_date)

                        #  Aggregate emotions for various perspective
                        happy += data['Happy']
                        angry += data['Angry']
                        surprise += data['Surprise']
                        sad += data['Sad']
                        fear += data['Fear']

                        print("done.")

        #  Write the total
        writeToCSVFile(writer, TOTAL, happy, angry, surprise, sad, fear)

        #  Show the result
        showPieChart([happy, angry, surprise, sad, fear])

    #  Handle any error
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


##############################
#  Load CSV and Show result  #
##############################
def loadCSVAndShowResult():    
    try:
      #  Open CSV file in read mode
      with codecs.open(CSV_FILE_NAME, 'r', encoding = DEFAULT_ENCODING) as csvfile:

        #  Write CSV header and initialize necessary variables
        reader = csv.DictReader(csvfile)

        #  Loop row and aggregate the value for various emotions
        for data in reader:
            #  Look for the last line
            if  data[FIELD_NAMES[4]] == TOTAL:
                #  Show the result
                # print(data)
                showPieChart([float(data[FIELD_NAMES[5]]), float(data[FIELD_NAMES[6]]), float(data[FIELD_NAMES[7]]), float(data[FIELD_NAMES[8]]), float(data[FIELD_NAMES[9]])])

    #  Handle any error
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise


def main():
    #parseHTMLAndShowResult()
    loadCSVAndShowResult()

        
if __name__ == "__main__":
    main()