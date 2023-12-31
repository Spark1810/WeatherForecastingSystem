import streamlit as st
import datetime
import requests
from plotly import graph_objects as go
import pandas as pd
import numpy as np
import pickle
from PIL import Image
import time


# Security
#passlib,hashlib,bcrypt,scrypt
import hashlib
def make_hashes(password):
        return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password,hashed_text):
        if make_hashes(password) == hashed_text:
                return hashed_text
        return False

def forecast():
    city = st.text_input("ENTER THE NAME OF THE CITY ")
    unit = st.selectbox("SELECT TEMPERATURE UNIT ", ["Celsius", "Fahrenheit"])
    speed = st.selectbox("SELECT WIND SPEED UNIT ", ["Metre/sec", "Kilometre/hour"])
    graph = st.radio("SELECT GRAPH TYPE ", ["Bar Graph", "Line Graph"])
    if unit == "Celsius":
        temp_unit = " °C"
    else:
        temp_unit = " °F"
    if speed == "Kilometre/hour":
        wind_unit = " km/h"
    else:
        wind_unit = " m/s"

    api = "9b833c0ea6426b70902aa7a4b1da285c"  # api key of open weather map
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api}"
    response = requests.get(url)
    x = response.json()
    if st.button("SUBMIT"):
        try:
            lon = x["coord"]["lon"]
            lat = x["coord"]["lat"]
            ex = "current,minutely,hourly"
            url2 = f'https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&exclude={ex}&appid={api}'
            res = requests.get(url2)
            y = res.json()

            maxtemp = []
            mintemp = []
            pres = []
            humd = []
            wspeed = []
            desc = []
            cloud = []
            rain = []
            dates = []
            sunrise = []
            sunset = []
            cel = 273.15

            for item in y["daily"]:

                if unit == "Celsius":
                    maxtemp.append(round(item["temp"]["max"] - cel, 2))
                    mintemp.append(round(item["temp"]["min"] - cel, 2))
                else:
                    maxtemp.append(round((((item["temp"]["max"] - cel) * 1.8) + 32), 2))
                    mintemp.append(round((((item["temp"]["min"] - cel) * 1.8) + 32), 2))

                if wind_unit == "m/s":
                    wspeed.append(str(round(item["wind_speed"], 1)) + wind_unit)
                else:
                    wspeed.append(str(round(item["wind_speed"] * 3.6, 1)) + wind_unit)

                pres.append(item["pressure"])
                humd.append(str(item["humidity"]) + ' %')

                cloud.append(str(item["clouds"]) + ' %')
                rain.append(str(int(item["pop"] * 100)) + '%')

                desc.append(item["weather"][0]["description"].title())

                d1 = datetime.date.fromtimestamp(item["dt"])
                dates.append(d1.strftime('%d %b'))

                sunrise.append(datetime.datetime.utcfromtimestamp(item["sunrise"]).strftime('%H:%M'))
                sunset.append(datetime.datetime.utcfromtimestamp(item["sunset"]).strftime('%H:%M'))

            def bargraph():
                fig = go.Figure(data=
                [
                    go.Bar(name="Maximum", x=dates, y=maxtemp, marker_color='crimson'),
                    go.Bar(name="Minimum", x=dates, y=mintemp, marker_color='navy')
                ])
                fig.update_layout(xaxis_title="Dates", yaxis_title="Temperature", barmode='group',
                                  margin=dict(l=70, r=10, t=80, b=80), font=dict(color="white"))
                st.plotly_chart(fig)

            def linegraph():
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=dates, y=mintemp, name='Minimum '))
                fig.add_trace(go.Scatter(x=dates, y=maxtemp, name='Maximimum ', marker_color='crimson'))
                fig.update_layout(xaxis_title="Dates", yaxis_title="Temperature", font=dict(color="white"))
                st.plotly_chart(fig)

            icon = x["weather"][0]["icon"]
            current_weather = x["weather"][0]["description"].title()

            if unit == "Celsius":
                temp = str(round(x["main"]["temp"] - cel, 2))
            else:
                temp = str(round((((x["main"]["temp"] - cel) * 1.8) + 32), 2))

            col1, col2 = st.columns(2)
            with col1:
                st.write("## Current Temperature ")
            with col2:
                st.image(f"http://openweathermap.org/img/wn/{icon}@2x.png", width=70)

            col1, col2 = st.columns(2)
            col1.metric("TEMPERATURE", temp + temp_unit)
            col2.metric("WEATHER", current_weather)
            st.subheader(" ")

            if graph == "Bar Graph":
                bargraph()

            elif graph == "Line Graph":
                linegraph()

            table1 = go.Figure(data=[go.Table(header=dict(
                values=[
                    '<b>DATES</b>',
                    '<b>MAX TEMP<br>(in' + temp_unit + ')</b>',
                    '<b>MIN TEMP<br>(in' + temp_unit + ')</b>',
                    '<b>CHANCES OF RAIN</b>',
                    '<b>CLOUD COVERAGE</b>',
                    '<b>HUMIDITY</b>'],
                line_color='black', fill_color='royalblue', font=dict(color='white', size=14), height=32),
                cells=dict(values=[dates, maxtemp, mintemp, rain, cloud, humd],
                           line_color='black',
                           fill_color=['paleturquoise', ['palegreen', '#fdbe72'] * 7], font_size=14, height=32
                           ))])

            table1.update_layout(margin=dict(l=10, r=10, b=10, t=10), height=328)
            st.write(table1)

            table2 = go.Figure(data=[go.Table(columnwidth=[1, 2, 1, 1, 1, 1], header=dict(
                values=['<b>DATES</b>', '<b>WEATHER CONDITION</b>', '<b>WIND SPEED</b>', '<b>PRESSURE<br>(in hPa)</b>',
                        '<b>SUNRISE<br>(in UTC)</b>', '<b>SUNSET<br>(in UTC)</b>']
                , line_color='black', fill_color='royalblue', font=dict(color='white', size=14), height=36),
                                              cells=dict(values=[dates, desc, wspeed, pres, sunrise, sunset],
                                                         line_color='black',
                                                         fill_color=['paleturquoise', ['palegreen', '#fdbe72'] * 7],
                                                         font_size=14, height=36))])

            table2.update_layout(margin=dict(l=10, r=10, b=10, t=10), height=360)
            st.write(table2)

        except KeyError:
            st.error(" Invalid city!!  Please try again !!")


# DB Management
import sqlite3 
conn = sqlite3.connect('data.db')
c = conn.cursor()
# DB  Functions
def create_usertable():
        c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username,password):
        c.execute('INSERT INTO userstable(username,password) VALUES (?,?)',(username,password))
        conn.commit()

def login_user(username,password):
        c.execute('SELECT * FROM userstable WHERE username =? AND password = ?',(username,password))
        data = c.fetchall()
        return data


def view_all_users():
        c.execute('SELECT * FROM userstable')
        data = c.fetchall()
        return data



def main():

        st.set_page_config(page_title='Weather Forecasting Prediction System', page_icon=":rainbow:")
        st.title("Weather Forecasting System 🌞🍃")
        activities = ["Introduction", "ADMIN LOGIN","USER LOGIN","SIGN UP",,"About Us"]
        choice = st.sidebar.selectbox("Select Activities", activities)
        if choice == 'Introduction':
            st.markdown(" Enhancing Your Weather-Related Decision Making")
            st.markdown("Weather plays a crucial role in our daily lives, influencing our activities, travel plans, and even our safety. Having access to accurate and up-to-date weather information is invaluable. This is where the Weather Forecasting App steps in, providing users with a comprehensive and reliable tool to stay informed about current and future weather conditions. The Weather Forecasting App is an innovative and user-friendly application designed to deliver precise weather forecasts directly to your fingertips. Leveraging advanced meteorological algorithms and real-time data from trusted sources, this app offers an intuitive and personalized weather experience. Users can access a wide range of features, including hourly and extended forecasts, severe weather alerts, radar imagery, and customizable notifications. With its sleek interface and interactive maps, the Weather Forecasting App allows users to visualize weather patterns and track storms with ease. The app also includes additional features like UV index, air quality information, and sunrise/sunset times to ensure users are well-prepared for their daily routines or outdoor activities. The Weather Forecasting App caters to a diverse range of users, from casual weather enthusiasts to professionals requiring precise weather information. It empowers individuals to make informed decisions, such as planning outdoor events, adjusting travel schedules, or preparing for severe weather events. In summary, the Weather Forecasting App is a powerful tool that combines accuracy, convenience, and comprehensive weather data to enhance your weather-related decision making. Stay ahead of changing conditions and maximize your safety and comfort with this essential app at your disposal.")
            st.subheader("Done By ... ")
            time.sleep(3)
            st.warning("Goto Menu Section To Login !")


        elif choice == "ADMIN LOGIN":
                 st.markdown("<h1 style='text-align: center;'>Admin Login Section</h1>", unsafe_allow_html=True)
                 user = st.sidebar.text_input('Username')
                 passwd = st.sidebar.text_input('Password',type='password')
                 if st.sidebar.checkbox("LOGIN"):

                         if user == "Admin" and passwd == 'admin123':

                                                st.success("Logged In as {}".format(user))
                                                st.subheader("User Profiles")
                                                user_result = view_all_users()
                                                clean_db = pd.DataFrame(user_result,columns=["Username","Password"])
                                                st.dataframe(clean_db)
                                                forecast()
                         else:
                                st.warning("Incorrect Admin Username/Password")
          
                         
                        

        elif choice == "USER LOGIN":
                st.markdown("<h1 style='text-align: center;'>User Login Section</h1>", unsafe_allow_html=True)
                username = st.sidebar.text_input("User Name")
                password = st.sidebar.text_input("Password",type='password')
                if st.sidebar.checkbox("LOGIN"):
                        # if password == '12345':
                        create_usertable()
                        hashed_pswd = make_hashes(password)

                        result = login_user(username,check_hashes(password,hashed_pswd))
                        if result:

                                st.success("Logged In as {}".format(username))
                                forecast()
                        else:
                                st.warning("Incorrect Username/Password")
                                st.warning("Please Create an Account if not Created")


        elif choice == "SIGN UP":
                st.subheader("Create New Account")
                new_user = st.text_input("Username")
                new_password = st.text_input("Password",type='password')

                if st.button("SIGN UP"):
                        create_usertable()
                        add_userdata(new_user,make_hashes(new_password))
                        st.success("You have successfully created a valid Account")
                        st.info("Go to User Login Menu to login")

        elif choice == "ABOUT US":
                st.header("CREATED BY _**NAME**_")
                st.subheader("UNDER THE GUIDENCE OF _**GUIDE DETAILS**_")


# ==========================================================================================================================


