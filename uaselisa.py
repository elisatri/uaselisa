#Python Packages/Libaries:
import googleapiclient.discovery
import pymysql
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
import re
import streamlit as st

#Google API key to retrieve youtube channel details

api_service_name = "youtube"
api_version = "v3"
api_key= "AIzaSyDOO-0Lj0WEBNX5hihD7gY_LMXPwgnDHUg"
youtube = googleapiclient.discovery.build(api_service_name, api_version, developerKey=api_key)

#Streamlit UI

with st.sidebar:
    st.title(":red[Youtube] [Data Harvesting & Warehousing using SQL]")
    st.subheader(':blue[Domain :] Social Media')
    st.subheader(':blue[Overview :]')
    st.markdown('''In this project, I built a simple UI using Streamlit,
                retrieved data from the YouTube API, stored the data in a SQL database as a data warehouse,
                and queried the data warehouse with SQL.
                The processed data was then displayed dynamically within the Streamlit app''')
    st.subheader(':blue[Skill Take Away :]')
    st.markdown(''' Python scripting,Data Collection,API integration,Data Management using SQL,Streamlit''')

channel_id=st.text_input("**Enter the channel ID in the below box:**")

if st.button("Extract the data and Store in MySQL"):

#Function to fetch the channel details

    def extract_channel_details(channel_id):
        response = youtube.channels().list(part="snippet,contentDetails,statistics",id=channel_id).execute()

        for i in response['items']:
            channel_data= {
                "channel_id":i['id'],
                "channel_name":i['snippet']['title'],
                "channel_description":i['snippet']['description'],
                "channel_videos_count":i['statistics']['videoCount'],
                "channel_subscribers_count":i['statistics']['subscriberCount'],
                "channel_views":i['statistics']['viewCount'],
                "channel_playlist_id":i['contentDetails']['relatedPlaylists']['uploads']}
        Channel_info=pd.DataFrame(channel_data,index=[0])
            
        return Channel_info
    
    Channel_details=extract_channel_details(channel_id)

#Function to fetch the Video Ids

    def extract_video_ids(channel_ids):
        video_ids=[]
        response=youtube.channels().list(part="contentDetails",id= channel_ids).execute()
        playlist_id=response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

        next_page_token=None
            
        while True:
            playlist_response = youtube.playlistItems().list(
                    part="snippet",
                    maxResults=50,
                    pageToken=next_page_token,
                    playlistId=playlist_id).execute()

            for i in range(len(playlist_response['items'])):
                video_ids.append(playlist_response['items'][i]['snippet']['resourceId']['videoId'])
            next_page_token=playlist_response.get('nextPageToken')

            if next_page_token is None:
                break       
        return video_ids

    Video_ids=extract_video_ids(channel_id)

#Function to convert Duration from ISO 8601 format to HH:MM:SS format

    def convert_duration(duration): 

        pattern = re.compile(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?')
        match = pattern.match(duration)
        if match:
                hours = int(match.group(1)) if match.group(1) else 0
                minutes = int(match.group(2)) if match.group(2) else 0
                seconds = int(match.group(3)) if match.group(3) else 0
                total_seconds = hours * 3600 + minutes * 60 + seconds
                return '{:02d}:{:02d}:{:02d}'.format(int(total_seconds / 3600), int((total_seconds % 3600) / 60), int(total_seconds % 60))
        else:
            return '00:00:00'
        
# Function to fetch video details for all video ids

    def extract_video_details(video_IDs):
        video_details=[]
        for video_id in video_IDs:
            response= youtube.videos().list(part="snippet,contentDetails,statistics",id=video_id).execute()

            for i in response['items']:
                    vid_data={"channel_id":i['snippet']['channelId'],
                        "video_id":i['id'],
                        "video_name":i['snippet']['title'],
                        "video_description":i['snippet']['description'],
                        "video_published_at":i['snippet']['publishedAt'],
                        "view_count":i['statistics']['viewCount'],
                        "like_count":i['statistics'].get('likeCount'),
                        "dislike_count":i.get('dislikeCount'),
                        "favorite_count":i['statistics']['favoriteCount'],
                        "comment_count":i['statistics'].get('commentCount'),
                        "duration":convert_duration(i['contentDetails']['duration']),
                        "thumbnail":i['snippet']['thumbnails']['default'] ['url'],
                        "caption_status":i['contentDetails']['caption'],
                        "tags":",".join(i['snippet'].get('tags',["na"]))}

                    video_details.append(vid_data)
            Video_info=pd.DataFrame(video_details)
#Converting Dateformat
            Video_info['video_published_at'] = pd.to_datetime(Video_info['video_published_at']).dt.strftime('%Y-%m-%d %H:%M:%S')
        return Video_info

    Video_details=extract_video_details(Video_ids)

#Function to fetch comment details for all video ids

    def extract_comment_info(videos_data):
        comment_details=[]

        try:
            for video_ids in videos_data:
                response=youtube.commentThreads().list(part="snippet",videoId=video_ids,maxResults=100).execute()

                for i in response['items']:
                    comm_data={"comment_id":i['id'],
                                "video_id": i['snippet']['videoId'],
                                "comment_text":i['snippet']['topLevelComment']['snippet']['textDisplay'],
                                "comment_author":i['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                "comment_published_at":i['snippet']['topLevelComment']['snippet']['publishedAt']}
                    comment_details.append(comm_data)
        except:
            pass
        
        Comment_info=pd.DataFrame(comment_details)
#Converting Dateformat
        Comment_info['comment_published_at'] = pd.to_datetime(Comment_info['comment_published_at']).dt.strftime('%Y-%m-%d %H:%M:%S')

        return Comment_info

    Comment_details=extract_comment_info(Video_ids)

#Table creation and uploads
    my_connection = pymysql.connect(host="127.0.0.1",user="root",password="1234")
    mycursor = my_connection.cursor()
    engine = create_engine("mysql+pymysql://root:1234@127.0.0.1/youtube")

# Channel_Details Table:

    mycursor.execute('create database if not exists youtube')
    mycursor.execute('use youtube')
    mycursor.execute('''create table if not exists channel( channel_id VARCHAR(50) PRIMARY KEY ,
                                    channel_name VARCHAR(1000),channel_description VARCHAR(1000),
                                    channel_videos_count BIGINT,channel_subscribers_count BIGINT,
                                    channel_views BIGINT,channel_playlist_id VARCHAR(50))''')
    my_connection.commit()
    Channel_details.to_sql('channel',engine,if_exists='append',index=False)

# Video_Details Table:
    mycursor.execute('create database if not exists youtube')
    mycursor.execute('use youtube')
    mycursor.execute('''create table if not exists video( channel_id VARCHAR(50),video_id VARCHAR(50) PRIMARY KEY ,
                                    video_name VARCHAR(1000) ,video_description VARCHAR(10000),video_published_at DATETIME,view_count BIGINT,
                                    like_count BIGINT,dislike_count BIGINT,favorite_count BIGINT,comment_count BIGINT,
                                    duration VARCHAR(10),thumbnail VARCHAR(100),caption_status VARCHAR(50),tags VARCHAR(1000),FOREIGN KEY (channel_id) REFERENCES channel(channel_id))''')
    my_connection.commit()
    Video_details.to_sql('video',engine,if_exists='append',index=False)

# Comment_Details Table:
    mycursor.execute('create database if not exists youtube')
    mycursor.execute('use youtube')
    mycursor.execute('''create table if not exists Comment( video_id VARCHAR(50), comment_id VARCHAR(50),
                                comment_text VARCHAR(10000) ,comment_author VARCHAR(1000),comment_published_at DATETIME,FOREIGN KEY (video_id) REFERENCES video(video_id))''')
    my_connection.commit()
    Comment_details.to_sql('comment',engine,if_exists='append',index=False)

    engine.dispose()

    st.success('**Successfully uploaded in MySQL Database**')

# To View all Channels
tab1,tab2 = st.tabs(["View Channels", "Queries"])
with tab1:
    Check_channel = st.checkbox('**Show the Channel Details**')
    if Check_channel:
        my_connection = pymysql.connect(host="127.0.0.1",user="root",password="1234")
        mycursor = my_connection.cursor()
        mycursor.execute("select channel_name,channel_id from youtube.channel")
        channel_df= pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Channel_Id'])
        channel_df.drop_duplicates(inplace=True)
        channel_df.index += 1
        st.write(channel_df)

#Queries
with tab2:
    st.write("Select SQL Queries to show the output")

    SQL_Queries = st.selectbox("SQL Queries",
                               ("Select Your Questions",
                                    "1. What are the names of all the videos and their corresponding channels?",
                                    "2. Which channels have the most number of videos, and how many videos do they have?",
                                    "3. What are the top 10 most viewed videos and their respective channels?",
                                    "4. How many comments were made on each video, and what are their corresponding video names?",
                                    "5. Which videos have the highest number of likes, and what are their corresponding channel names?",
                                    "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?",
                                    "7. What is the total number of views for each channel, and what are their corresponding channel names?",
                                    "8. What are the names of all the channels that have published videos in the year 2022?",
                                    "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?",
                                    "10. Which videos have the highest number of comments, and what are their corresponding channel names?"),
                                    key="collection_question")
    
    #Query 1

    my_connection = pymysql.connect(host="127.0.0.1",user="root",password="1234")
    mycursor = my_connection.cursor()
    mycursor.execute('use youtube')

    if SQL_Queries == "1. What are the names of all the videos and their corresponding channels?":
        mycursor.execute("select c.channel_name,v.video_name from video as v inner join channel as c on v.channel_id = c.channel_id")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Video_name'])
        df.index += 1
        st.write(df)
    
    elif SQL_Queries == "2. Which channels have the most number of videos, and how many videos do they have?":
        mycursor.execute("select channel_name,channel_videos_count from channel order by channel_videos_count desc")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Video_count'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "3. What are the top 10 most viewed videos and their respective channels?":
        mycursor.execute("select c.channel_name,v.video_name,v.view_count from video as v inner join channel as c on v.channel_id = c.channel_id order by view_count desc limit 10")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Video_name','Most_viewed_video'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "4. How many comments were made on each video, and what are their corresponding video names?":
        mycursor.execute("select video_name,comment_count from video order by comment_count desc")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Video_name','Comment_count'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "5. Which videos have the highest number of likes, and what are their corresponding channel names?":
        mycursor.execute("select c.channel_name,sum(v.like_count) as Highest_likes from video as v inner join channel as c on v.channel_id=c.channel_id group by c.channel_name order by Highest_likes desc")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Highest_Likes'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "6. What is the total number of likes and dislikes for each video, and what are their corresponding video names?":
        mycursor.execute("select video_name,like_count from video order by like_count desc")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Video_name','Like_count'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "7. What is the total number of views for each channel, and what are their corresponding channel names?":
        mycursor.execute("select channel_name,channel_views from channel order by channel_views desc")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','View_count'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "8. What are the names of all the channels that have published videos in the year 2022?":
        mycursor.execute("select distinct channel_name from channel as c inner join video as v on v.channel_id=c.channel_id where video_published_at between '2022-01-01 00:00:00' and '2022-12-31 23:59:59'")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "9. What is the average duration of all videos in each channel, and what are their corresponding channel names?":
        mycursor.execute("select c.channel_name,TIME_FORMAT(SEC_TO_TIME(AVG(TIME_TO_SEC(TIME(v.duration)))), '%H:%i:%s') as average_duration from video as v inner join channel as c on v.channel_id=c.channel_id group by c.channel_name")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Average_duration'])
        df.index += 1
        st.write(df)

    elif SQL_Queries == "10. Which videos have the highest number of comments, and what are their corresponding channel names?":
        mycursor.execute("select c.channel_name,sum(v.comment_count) as Highest_comment from video as v inner join channel as c on v.channel_id=c.channel_id group by c.channel_name order by Highest_comment desc")
        df = pd.DataFrame(mycursor.fetchall(),columns=['Channel_name','Highest_comment'])
        df.index += 1
        st.write(df)





