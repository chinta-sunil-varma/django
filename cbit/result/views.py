from multiprocessing.sharedctypes import Value
from django.http import HttpResponse
from django.shortcuts import render
from .models import login
from django.contrib import messages
import sys
from fake_user_agent.main import user_agent
import requests
from bs4 import BeautifulSoup
import pandas as pd

# Create your views here.


def base(request):

    dict = {}
    if request.method == 'POST':
        username = request.POST.get('usr')
        password = request.POST.get('pass')
        sem = request.POST.get('sem')
        qur = login(username=username, password=password)
        qur.save()
        ua = user_agent('chrome')


        headers={'User-Agent':str(ua)}
        with requests.Session() as s:
            url="https://erp.cbit.org.in/beeserp/Login.aspx"
            g=s.get(url,headers=headers)
            src=g.content
            soup=BeautifulSoup(src,'lxml')
            lis=soup.find_all('input',{'type':'hidden'})
            a=[]
            for i in lis:
                a.append(i.attrs['value'])
            # your ERP Website credentials
            # username='160120737114'
            # password='iamthebestcoder123@'
            

            payload={'__VIEWSTATE':a[3],'__VIEWSTATEGENERATOR':a[4],'__EVENTVALIDATION':a[5],'txtUserName':username,'btnNext':'Next'}
            post2 = s.post('https://erp.cbit.org.in/beeserp/login.aspx', data=payload,allow_redirects=True)

            # print('successfully bypassed username page')
            res=post2.content
            soup1=BeautifulSoup(res,'lxml')
            lis1=soup1.find_all('input',{'type':'hidden'})
            b=[]
            for i in lis1:
                b.append(i.attrs['value'])

            payload1 = { '__VIEWSTATE': b[0],
                    '__VIEWSTATEGENERATOR': b[1], '__EVENTVALIDATION': b[2],'txtPassword': password, 'btnSubmit':'Submit'
                    }
            print(post2.request.url)
            post1 = s.post(post2.request.url, data=payload1)

            # print('suceesfully bypassed password page')

            overall_result=s.get('https://erp.cbit.org.in/beeserp/StudentLogin/Student/OverallMarksSemwise.aspx')

            
            
            
            semwise = overall_result.content
            soup2 = BeautifulSoup(semwise, 'lxml')
            lis2 = soup2.find_all('input', {'type': 'hidden'})
            value = []
            for x in lis2:
                    value.append(x.attrs['value'])
            
            button_value = 'ctl00$cpStud$btn' + sem
            if (sem == '1'):
                    sem_val = 'I '
            elif (sem == '2'):
                    sem_val = 'II '
            elif (sem == '3'):
                    sem_val = 'III '
            elif (sem == '4'):
                    sem_val = 'IV '
            elif (sem == '5'):
                    sem_val = 'V '
            elif (sem == '6'):
                    sem_val = 'VI '
            elif (sem == '7'):
                    sem_val = 'VII '
            elif (sem == '8'):
                    sem_val = 'VIII '
            else:
                    
                    sys.exit()
            
            btn_val = sem_val + 'SEM'
            payload2 = {'__VIEWSTATE': value[0], '__VIEWSTATEGENERATOR': value[1], button_value: btn_val}
            sem_page = s.post(overall_result.request.url, data=payload2)

                # print('succesfully submited given sem value')
            soup2=BeautifulSoup(sem_page.content,'lxml')
            gpa=soup2.find_all(class_='MessageLabelRed')
                # print(gpa)
            cgpa=gpa[4].text
            sgpa=gpa[3].text

            tables=pd.read_html(sem_page.text)


            tables[6].loc[len(tables[6].index)]=['','',sgpa,cgpa,'','','']
            tables[6]=tables[6].set_index('SlNo')
            html=tables[6].to_html()
            tables[6].to_csv('static\\'+username+'.csv')
            
            dict['html']=html+'<a href=static\\'+username+'.csv'+' download> click here to download the file</a>'
                
            
    return render(request,'base.html',dict)