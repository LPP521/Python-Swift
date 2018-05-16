#coding:utf-8
from django.shortcuts import render,HttpResponse,render_to_response,HttpResponseRedirect
from swiftclient import client
from .forms import FileForm
from keystoneclient.v3 import client as keystone_client
import os
# Create your views here.

_authurl = 'http://192.168.56.111:5000/v3/'
_auth_version = '3'
_user = 'admin'
_key = 'swift'
_os_options = {
    'user_domain_name': 'default',
    'project_domain_name': 'default',
    'project_name': 'admin'
}

conn = client.Connection(
    authurl=_authurl,
    user=_user,
    key=_key,
    os_options=_os_options,
    auth_version=_auth_version
)

def get_keystone_conn():
    conn = keystone_client.Client(user_domain_name='default',
                                  #username=os.environ['OS_USERNAME'],
                                  username='admin',
                                  #password=os.environ['OS_PASSWORD'],
                                  password='swift',
                                  project_domain_name='default',
                                  project_name='admin',
                                  auth_url='http://192.168.56.111:35357/v3/'
                                  )
    return conn

keystone_conn = get_keystone_conn()

def register(request):
    unames = get_user_list().keys()
    print unames
    if request.method == 'POST':
        uname = request.POST.get('username')
        if request.POST.get('first')==request.POST.get('second')and request.POST.get('first')!=''and uname!='':
            if uname in unames:
                return HttpResponseRedirect('/pyswift')
            else:
                upwd = request.POST.get('second')
                domain_id="3f245683dfbc46f0908abdf6373a9668"
                project_name='admin'

                #use admin conn create a user
                keystone_conn.users.create(uname,domain_id,project_name,upwd)

                #conn.users.add_to_group(get_user_list()[unname],'3f245683dfbc46f0908abdf6373a9668')
                return  HttpResponseRedirect('/pyswift/login')
        else:
            return render_to_response('pyswift/register.html')
    else:
        return render_to_response('pyswift/register.html')

def get_user_list():
    user_lists={}
    users = keystone_conn.users.list()
    for u in users:
        user_lists[u.name]=u.id
    return user_lists
get_user_list()

def index(request):
    resp_headers, containers = conn.get_account()
    #resp_headers, containers_file = conn.get_container()
    #print("Response headers: %s" % resp_headers)
    #for container in containers:
    return render_to_response('pyswift/index.html',{'containers':containers})

def login(request):
    errors=[]
    unames = get_user_list().keys()
    if request.method == 'POST':
        if not request.POST.get('username')or not request.POST.get('password'):
            errors.append('Your username or password is empty')
        elif request.POST.get('username') in unames and request.POST.get('password') in unames:
            return HttpResponseRedirect('/pyswift')
        else:
            errors.append('Your username or password is incorrectly')
    else:
        return render_to_response('pyswift/login.html')
    return render_to_response('pyswift/login.html',{'errors':errors})

def perview(request,container_name,file_name=None):
    reminder = None
    fileform = FileForm(request.POST,request.FILES)
    if request.method == 'POST':
        if request.POST.get('delete') == 'Delete':
            conn.delete_object(container_name,file_name)
        elif request.POST.get('download') == 'Download':
            resp_headers, file_contents = conn.get_object(container_name,file_name)
            f = open('/home/downfile/downfile.txt','w')
            f.write(file_contents)
            f.close
            reminder = 1
        elif request.POST.get('upload') == 'Upload':
            fileform = FileForm(request.POST,request.FILES)
            if fileform.is_valid():
                uploadfile = request.FILES['onefile']
                lines = uploadfile.read()
                conn.put_object(container_name, 'ceshi.txt', lines)
        else:
            fileform=FileForm
    resp_headers, containers_file = conn.get_container(container_name)
    return render_to_response('pyswift/perview.html',{'containers_file':containers_file,'container_name':container_name,'fileform':fileform,'reminder':reminder})

def content(request,container_name,file_name):
    resp_headers, file_content = conn.get_object(container_name,file_name)
    return render_to_response('pyswift/content.html', {'file_content': file_content,'container_name':container_name})