# ! /usr/bin/env python
# coding=utf-8
import requests
import json
import os
import pprint
import copy
import sys


class Api(object):

    def __init__(self, render_server):
        self.url = 'https://%s/api/v1/task' % (render_server)
        self.headers = {"Content-Type": "application/json"}

    def post(self, data):
        # print "\n"
        # print "Post data:"
        # pprint.pprint(data)
        # print "\n"

        if isinstance(data, dict):
            data = json.dumps(data)
        r = requests.post(self.url, headers=self.headers,
                          data=data)
        if r.status_code == 200:
            return r.json()
        elif r.status_code == 405:
            print r.status_code
            raise Exception("Connect server error.")
        else:
            print r.status_code
            raise Exception("Server internal error.")


class Fox(Api):
    root = os.path.dirname(os.path.abspath(__file__))
    ascp_exe = os.path.join(root, "aspera", "ascp.exe")

    def __init__(self, render_server, account, access_key,
                 aspera_server, aspera_password, language="en"):
        Api.__init__(self, render_server)
        self.data = {"head": {"access_key": access_key,
                              "account": account,
                              "msg_locale": language,
                              "action": ""},
                     "body": {}}

        self.login()
        self.aspera_server = aspera_server
        self.aspera_upload = self.account_id + "_upload"
        self.aspera_download = self.account_id + "_download"
        self.aspera_password = aspera_password

    def login(self):
        result = self.get_users()
        if result:
            self.account_id = result[0]["id"]
        else:
            raise Exception("account or access_key is not valid.")

    def submit_task(self, project_name, input_scene_path, frames):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "create_task"

        data["body"]["project_name"] = project_name
        data["body"]["submit_account"] = data["head"]["account"]
        data["body"]["input_scene_path"] = input_scene_path.replace(":", "").replace("\\", "/")
        data["body"]["frames"] = frames

        project = self.get_projects(project_name)
        if not project:
            raise Exception("Project <%s> doesn't exists." % (project_name))

        plugins = project[0]["plugins"]
        if not plugins:
            raise Exception("Project <%s> doesn't have any plugin settings." % (project_name))

        default_plugin = [i for i in plugins
                          if "is_default" in i if i["is_default"] == '1']

        if len(plugins) == 1:
            default_plugin = plugins

        if not default_plugin:
            raise Exception("Project <%s> doesn't have a default plugin settings." % (project_name))

        data["body"]["cg_soft_name"] = default_plugin[0]["cg_soft_name"]
        if "plugin_name" in default_plugin[0]:
            data["body"]["plugin_name"] = default_plugin[0]["plugin_name"]

        result = self.post(data)
        if result["head"]["result"] == '0':
            return int(result["body"]["data"][0]["task_id"])
        else:
            return -1

    def get_users(self, has_child_account=0):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "query_customer"

        if not has_child_account:
            data["body"]["login_name"] = data["head"]["account"]

        result = self.post(data)
        if result["head"]["result"] == "0":
            return result["body"]["data"]
        else:
            return []

    def get_projects(self, project_name=None):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "query_project"

        if project_name:
            data["body"]["project_name"] = project_name

        result = self.post(data)
        if result["head"]["result"] == "0":
            return result["body"]["data"]
        else:
            return []

    def get_tasks(self, task_id=None, project_name=None, has_frames=0):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "query_task"

        if project_name:
            data["body"]["project_name"] = project_name

        if task_id:
            data["body"]["task_id"] = str(task_id)

        if has_frames:
            data["body"]["is_jobs_included"] = "1"

        result = self.post(data)
        if result["head"]["result"] == "0":
            return result["body"]["data"]
        else:
            return []

    def upload(self, path_list, skip_same=1, user=None, password=None):
        user = user if user else self.aspera_upload
        os.environ["ASPERA_SCP_PASS"] = password if password else self.aspera_password
        overwrite = "older" if skip_same else "always"

        result = {}
        for i in set(path_list):
            if os.path.exists(i):
                server_path = os.path.dirname(i).replace(":", "")
                cmd = "echo y | \"%s\" -P 33001 -O 33001 -d -p -l 1000000 " \
                      "--overwrite=%s \"%s\" %s@%s:/%s" % (self.ascp_exe,
                                                           overwrite,
                                                           i,
                                                           user,
                                                           self.aspera_server,
                                                           server_path)
                print cmd
                sys.stdout.flush()
                result[i] = os.system(cmd)
            else:
                result[i] = -1

        return result

    def download(self, task_id, local_path, skip_same=1, user=None, password=None):
        user = user if user else self.aspera_download
        os.environ["ASPERA_SCP_PASS"] = password if password else self.aspera_password
        overwrite = "older" if skip_same else "always"

        task = self.get_tasks(task_id)
        if task:
            server_path = "%s_%s" % (task_id, os.path.splitext(os.path.basename(task[0]["scene_name"]))[0])
            cmd = "echo y | \"%s\" -P 33001 -O 33001 -d -p -l 1000000 " \
                  "--overwrite=%s %s@%s:/%s \"%s\"" % (self.ascp_exe,
                                                       overwrite,
                                                       user,
                                                       self.aspera_server,
                                                       server_path,
                                                       local_path)
            print cmd
            sys.stdout.flush()
            return os.system(cmd)
        else:
            return -1

    def get_server_files(self):
        ''

    def delete_server_files(self):
        ''
