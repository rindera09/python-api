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
        self.debug = 0

    def post(self, data):
        if self.debug:
            print "\n"
            print "Post data:"
            pprint.pprint(data)
            print "\n"

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

    def __init__(self, render_server, account, access_key, language="en"):
        Api.__init__(self, render_server)
        self.data = {"head": {"access_key": access_key,
                              "account": account,
                              "msg_locale": language,
                              "action": ""},
                     "body": {}}
        self.login()
        self.rayvision_exe = os.path.join("rayvision", "rayvision_transmitter")
        self._init_upload_download_config()

    def login(self):
        result = self.get_users()
        if result:
            self.account_id = result[0]["id"]
        else:
            raise Exception("account or access_key is not valid.")

    def _init_upload_download_config(self):
        user_info = self.get_users()[0]
        self.upload_id = user_info["upload_id"]
        self.download_id = user_info["download_id"]
        self.transports = user_info["transports"]

        if self.transports:
            self.engine_type = self.transports[0]["engine"]
            self.server_name = self.transports[0]["server"]
            self.server_ip = self.transports[0]["ip"]
            self.server_port = self.transports[0]["port"]

    def submit_task(self, **kwargs):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "create_task"

        if kwargs:
            for i in kwargs:
                data["body"][i] = kwargs[i]
            if "project_name" not in kwargs:
                raise Exception("Missing project_name args, please check.")
            if "input_scene_path" not in kwargs:
                raise Exception("Missing input_scene_path args, please check.")
            if "frames" not in kwargs:
                raise Exception("Missing frames, please check args.")

        data["body"]["input_scene_path"] = data["body"]["input_scene_path"].replace(":", "").replace("\\", "/")
        data["body"]["submit_account"] = data["head"]["account"]

        project = self.get_projects(kwargs["project_name"])
        if not project:
            raise Exception("Project <%s> doesn't exists." % (kwargs["project_name"]))

        plugins = project[0]["plugins"]
        no_plugin = True
        for i in plugins:
            if i:
                no_plugin = False
                break
        if no_plugin:
            raise Exception("Project <%s> doesn't have any plugin settings." % (kwargs["project_name"]))

        default_plugin = [i for i in plugins
                          if "is_default" in i if i["is_default"] == '1']

        if len(plugins) == 1:
            default_plugin = plugins

        if not default_plugin:
            raise Exception("Project <%s> doesn't have a default plugin settings." % (kwargs["project_name"]))

        data["body"]["cg_soft_name"] = default_plugin[0]["cg_soft_name"]
        if "plugin_name" in default_plugin[0]:
            data["body"]["plugin_name"] = default_plugin[0]["plugin_name"]

        result = self.post(data)
        if result["head"]["result"] == '0':
            return int(result["body"]["data"][0]["task_id"])
        else:
            pprint.pprint(result)
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

    def get_tasks(self, task_id=None, project_name=None, has_frames=0, task_filter={}):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "query_task"

        if project_name:
            data["body"]["project_name"] = project_name

        if task_id:
            data["body"]["task_id"] = str(task_id)

        if has_frames:
            data["body"]["is_jobs_included"] = "1"

        if task_filter:
            for i in task_filter:
                data["body"][i] = task_filter[i]

        result = self.post(data)
        if result["head"]["result"] == "0":
            return result["body"]["data"]
        else:
            return []

    def upload(self, local_path_list, server_path='/', **kwargs):

        transmit_type = "upload_files"
        result = {}
        for i in set(local_path_list):
            if os.path.exists(i):
                local_path = i
                cmd = "echo y | %s %s %s %s %s %s %s %s %s %s" % (self.rayvision_exe,
                                                                  self.engine_type,
                                                                  self.server_name,
                                                                  self.server_ip,
                                                                  self.server_port,
                                                                  self.upload_id,
                                                                  self.account_id,
                                                                  transmit_type,
                                                                  local_path,
                                                                  server_path)
                print cmd
                result[i] = True
                sys.stdout.flush()
                result[i] = os.system(cmd)
            else:
                result[i] = False
        return result

    def download(self, task_id, local_path, **kwargs):

        transmit_type = "download_files"
        task = self.get_tasks(task_id)

        if task:
            input_scene_path = task[0]["input_scene_path"]
            server_path = "%s_%s" % (task_id, os.path.splitext(os.path.basename(input_scene_path))[0].strip())
            cmd = "echo y | %s %s %s %s %s %s %s %s %s %s" % (self.rayvision_exe,
                                                              self.engine_type,
                                                              self.server_name,
                                                              self.server_ip,
                                                              self.server_port,
                                                              self.download_id,
                                                              self.account_id,
                                                              transmit_type,
                                                              local_path,
                                                              server_path)
            print cmd
            sys.stdout.flush()
            return os.system(cmd)
        else:
            return False

    def get_server_files(self):
        ''

    def delete_server_files(self):
        ''

    """ NO 7.2.3
        :param project_name: the name of the project you want to create
        :param kwargs:  can be used to pass more arguments, not necessary
                        including project_path, render_os, remark, sub_account

    """
    def create_project(self, project_name, **kwargs):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "create_project"

        if not project_name:
            raise Exception("Missing project_name, please check")
        data["body"]["project_name"] = project_name
        for key, value in kwargs.items():
            data["body"][key] = value

        result = self.post(data=data)
        if result["head"]["result"] == '0':
            project_id = int(result["body"]["project_id"])
            self._message_output("INFO", "Project ID: {0}".format(project_id))
            return True, project_id
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    def _message_output(self, msg_type=None, msg=None):
        print "[{0}]: {1}".format(msg_type, msg)

    """ NO: 7.2.2  Query plugins
        :param kwargs:  can be used to pass more arguments, not necessary
                        including cg_soft_name, plugin_name
        Here some examples::
                get_plugin()
                get_plugin(cg_soft_name="3ds Max 2010")
                get_plugin(cg_soft_name="3ds Max 2010", plugin_name="finalrender 3.5sp6")
    """
    def get_plugins_available(self, **kwargs):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "query_plugin"
        for key, value in kwargs.items():
            data["body"][key] = value

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            self._save_list2file(result["body"], "plugins.txt")
            return True, result["body"]
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    def _save_list2file(self, list_data, file_name, remark="\n"):
        basedir = os.path.abspath(os.path.dirname(__file__))
        save_path = os.path.join(basedir, file_name)
        with open(save_path, "a+") as f:
            if remark:
                f.write(remark)
            for line in list_data:
                f.write(str(line) + "\n")
        print "[INFO]:" + save_path + " has saved."

    """ NO 7.2.4 Add config for project
        :param project_id:  the id of the existed project you choose
        :param cg_soft_name:  the software you use
        :param plugin_name:  the plugin you use
        :param is_default:  make it as default setting
        :param kwargs: can  be used to pass more arguments, not necessary

    """
    def add_project_config(self, project_id, cg_soft_name, plugin_name=None,
                           is_default=0, **kwargs):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "operate_project"
        data["body"]["operate_type"] = 0

        data["body"]["project_id"] = int(project_id)
        data["body"]["cg_soft_name"] = cg_soft_name
        if plugin_name:
            data["body"]["plugin_name"] = plugin_name
        data["body"]["is_default"] = is_default
        for key, value in kwargs.items():
            data["body"][key] = value

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            return True
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    """ NO 7.2.4 Delete config for project
        :param project_id: the id of the existed project you choose
        :param config_id: the id of configuration you want to delete
                          if not pass this argument it will delete all
                          you can use "get_project_info" to get config_id
        :param kwargs: can be used to pass more arguments, not necessary

    """
    def delete_project_config(self, project_id, config_id=None, **kwargs):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "operate_project"
        data["body"]["operate_type"] = 2

        data["body"]["project_id"] = int(project_id)
        if config_id:
            data["body"]["config_id"] = int(config_id)
        for key, value in kwargs.items():
            data["body"][key] = value

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            self._message_output("INFO", "configuration delete")
            return True
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    """ NO 7.2.4 Modify config for project
        :param project_id:  the id of the existed project you choose
        :param config_id:  the id of configuration you want to delete
                           if not pass this argument it will delete all
                           you can use "get_projects" to get config_id
        :param cg_soft_name:  the software you use
        :param plugin_name:  the plugin you use
        :param is_default:  make it as default setting, just one default allowed
        :param kwargs: can  be used to pass more arguments, not necessary

    """
    def modify_project_config(self, project_id, config_id, cg_soft_name,
                              plugin_name=None, is_default=None, **kwargs):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "operate_project"
        data["body"]["operate_type"] = 1

        data["body"]["project_id"] = int(project_id)
        data["body"]["config_id"] = int(config_id)
        data["body"]["cg_soft_name"] = cg_soft_name
        if plugin_name is not None:
            data["body"]["plugin_name"] = plugin_name
        if is_default:
            data["body"]["is_default"] = int(is_default)
        for key, value in kwargs.items():
            data["body"][key] = value

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            self._message_output("INFO", "modify the configuration")
            return True
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    """ NO 7.1.3 Restart the tasks
        :param task_id:  the tasks you what to restart
        :param restart_type:  0 -- restart the failed frames
                              1 -- restart the frames that give up
                              2 -- restart the finished frames
                              3 -- restart the start frames
                              4 -- restart the waiting frames
        Here some example::  restart_tasks("123", "0")
                             restart_tasks(["123", "456"], "3")
    """
    def restart_tasks(self, task_id, restart_type="0"):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "operate_task"
        data["body"]["operate_order"] = "1"
        data["body"]["restart_type"] = str(restart_type)
        if isinstance(task_id, list) and len(task_id) > 1:
            task_id = ''.join([str(id) + ',' for id in task_id[:-1]]) + str(task_id[-1])
        data["body"]["task_id"] = str(task_id)

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            self._message_output("INFO", "task {0} restart.".format(task_id))
            return True
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    """ NO 7.1.3 Stop the tasks
        :param task_id:  the tasks you what to pause

        Here some example::  stop_tasks(123)
                             stop_tasks("123")
                             stop_tasks(["123", "456"])
                             stop_tasks([123, 456])
    """
    def stop_tasks(self, task_id):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "operate_task"
        data["body"]["operate_order"] = "0"
        if isinstance(task_id, list) and len(task_id) > 1:
            task_id = ''.join(map(lambda id: str(id) + ",", task_id[:-1])) + str(task_id[-1])
        data["body"]["task_id"] = str(task_id)

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            self._message_output("INFO", "task {0} paused.".format(task_id))
            return True
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    """ NO 7.1.3 Delete the tasks
        :param task_id:  the tasks you what to delete

        Here some example::  delete_tasks(123)
                             delete_tasks("123")
                             delete_tasks(["123", "456"])
                             delete_tasks([123, 456])
    """
    def delete_tasks(self, task_id):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "operate_task"
        data["body"]["operate_order"] = "2"
        if isinstance(task_id, list) and len(task_id) > 1:
            task_id = ''.join(map(lambda id: str(id) + ",", task_id[:-1])) + str(task_id[-1])
        data["body"]["task_id"] = str(task_id)

        result = self.post(data=data)
        if result["head"]["result"] == "0":
            self._message_output("INFO", "task {0} deleted.".format(task_id))
            return True
        else:
            self._message_output("ERROR", result["head"]["error_message"])
            return False

    """ Get the plugins of the project
        :param project_name:  the name of the project
    """
    def get_project_plugins_config(self, project_name):
        data = copy.deepcopy(self.data)
        data["head"]["action"] = "query_project"

        if not project_name:
            self._message_output("WARNING", "Mising project name")
            return []

        data["body"]["project_name"] = project_name

        result = self.post(data)
        plugins = []
        if result["body"]["data"]:
            plugins = result["body"]["data"][0]["plugins"]

        if result["head"]["result"] == "0":
            self._message_output("INFO", "Query plugins config id:")
            return plugins
        else:
            self._message_output("WARNING", result["head"]["error_message"])
            return []
