import cv2
import numpy as np
import pandas as pd
import av
import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

from PIL import Image
import sqlite3
import torch

import sys
sys.path.append('modules')
sys.path.append('exp')
from modules.load_model import load 
from models.experimental import attempt_load


conn = sqlite3.connect('inventory1.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS drinks (time TEXT, name TEXT, countt NUMERIC)')

def main():
        st.title("Cold Drinks Inventory Management System")
        choice=st.selectbox("Mode",["None","Staff"])

        def get_opened_image(image):
            return Image.open(image)

        RTC_CONFIGURATION = RTCConfiguration(
            {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )

        if choice=='Staff':
            st.title("Staff")
            date1=st.sidebar.date_input("Date")
            confidence_threshold=st.sidebar.slider("Confidence threshold",0.0,1.0)
            mode=st.sidebar.radio("View mode",['video','data','image'])

            if mode=="video":
                st.title("Object detection video")
                webrtc_ctx = webrtc_streamer(
                key="WYH",
                mode=WebRtcMode.SENDRECV,
                rtc_configuration=RTC_CONFIGURATION,
                media_stream_constraints={"video": True, "audio": False},
                async_processing=True,)
                st.checkbox("Store")
                st.checkbox("Show the detected labels")

            if mode=="image":
                img_file_buffer = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])
                detect=st.checkbox("Show the detected labels")
                if detect:
                    if img_file_buffer is not None: 
                        image = np.array(Image.open(img_file_buffer)) 
                        image = cv2.resize(image, (640, 640))
                        model=attempt_load('exp/best.pt' ,map_location='cpu')
                        image_box, counting = load(model, image, confidence_threshold,640)  
                        st.image(
                                image_box, caption=f"Processed image", use_column_width=True,
                            )
                        C = {k: v for k, v in counting.items() if v > 0}
                        data = pd.DataFrame(C, index=['items'])
                        st.sidebar.table(data)
                        for namee, d in C.items():
                            c.execute('INSERT INTO drinks (time,name,countt) VALUES (?, ?, ?)',( date1, namee , d))
                            conn.commit()
                else:
                    if img_file_buffer is not None:
                        image=get_opened_image(img_file_buffer)
                        with st.expander("Selected Image",expanded=True):
                            st.image(img_file_buffer,use_column_width=True)
               


            if mode=="data":
                st.header("DATA")
            

                drinkname=st.text_input("Enter drink name")
                drinkcount=st.text_input("Enter count")
                date=st.date_input("Select date")
                

                if(st.button("SUBMIT")):
                        c.execute('INSERT INTO drinks (time,name,countt) VALUES (?, ?, ?)',( date, drinkname , drinkcount))
                        conn.commit()
                
                read_list1=[]  
                c.execute('SELECT time,name,countt FROM drinks')
                read_list1=c.fetchall()
                df1= pd.DataFrame(
                    read_list1,
                    columns=["time","name","count"]
                )
                st.table(df1) 

                read_list2=[]    
                c.execute('SELECT name,sum(countt) FROM drinks GROUP BY name ')
                read_list2=c.fetchall()
                df2 = pd.DataFrame(
                    read_list2,
                    columns=["name","count"]
                )
                st.table(df2)  
                

                choice1=st.sidebar.radio("Download mode",['None','CSV','excel'])

                if choice1=="CSV":
                    st.download_button(label='download csv',data=df2.to_csv() ,mime='text/csv' ,)

                elif choice1=="excel":
                    st.download_button(label='download excel',data="abc.xlsx" ,mime='text/xlsx')
main()
            


       









        
          
      

       

            
