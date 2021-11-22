#!/usr/bin/env python3
# -*-coding:UTF-8 -*

'''
    Blueprint Flask: crawler splash endpoints: dashboard, onion crawler ...
'''

import os
import sys
import json
import random

from flask import Flask, render_template, jsonify, request, Blueprint, redirect, url_for, Response, make_response
from flask_login import login_required, current_user, login_user, logout_user

sys.path.append('modules')
import Flask_config

# Import Role_Manager
from Role_Manager import create_user_db, check_password_strength, check_user_role_integrity
from Role_Manager import login_admin, login_analyst, login_read_only

sys.path.append(os.path.join(os.environ['AIL_BIN'], 'packages'))
import Tag

sys.path.append(os.path.join(os.environ['AIL_BIN'], 'lib'))
import item_basic
import Tracker

sys.path.append(os.path.join(os.environ['AIL_BIN'], 'core'))
import ail_2_ail

bootstrap_label = Flask_config.bootstrap_label

# ============ BLUEPRINT ============
ail_2_ail_sync = Blueprint('ail_2_ail_sync', __name__, template_folder=os.path.join(os.environ['AIL_FLASK'], 'templates/ail_2_ail'))

# ============ VARIABLES ============



# ============ FUNCTIONS ============
def api_validator(api_response):
    if api_response:
        return Response(json.dumps(api_response[0], indent=2, sort_keys=True), mimetype='application/json'), api_response[1]

def create_json_response(data, status_code):
    return Response(json.dumps(data, indent=2, sort_keys=True), mimetype='application/json'), status_code

# ============= ROUTES ==============

@ail_2_ail_sync.route('/settings/ail_2_ail', methods=['GET'])
@login_required
@login_admin
def ail_2_ail_dashboard():
    l_servers = ail_2_ail.get_all_running_sync_servers()
    l_servers = ail_2_ail.get_ail_instances_metadata(l_servers)
    return render_template("ail_2_ail_dashboard.html", l_servers=l_servers)

######################
#                    #
#### AIL INSTANCE ####

# # TODO: add more metadata => queues + connections
@ail_2_ail_sync.route('/settings/ail_2_ail/servers', methods=['GET'])
@login_required
@login_admin
def ail_servers():
    l_servers = ail_2_ail.get_all_ail_instances_metadata()
    return render_template("ail_servers.html", l_servers=l_servers)

@ail_2_ail_sync.route('/settings/ail_2_ail/server/view', methods=['GET'])
@login_required
@login_admin
def ail_server_view():
    ail_uuid = request.args.get('uuid')
    server_metadata = ail_2_ail.get_ail_instance_metadata(ail_uuid,sync_queues=True)
    server_metadata['sync_queues'] = ail_2_ail.get_queues_metadata(server_metadata['sync_queues'])

    return render_template("view_ail_server.html", server_metadata=server_metadata,
                                bootstrap_label=bootstrap_label)

@ail_2_ail_sync.route('/settings/ail_2_ail/server/add', methods=['GET', 'POST'])
@login_required
@login_admin
def ail_server_add():
    if request.method == 'POST':
        register_key = request.form.get("register_key")
        ail_uuid = request.form.get("ail_uuid")
        url = request.form.get("ail_url")
        description = request.form.get("ail_description")
        pull = request.form.get("ail_pull")
        push = request.form.get("ail_push")

        input_dict = {"uuid": ail_uuid, "url": url,
                        "description": description,
                        "pull": pull, "push": push}

        if register_key:
            input_dict['key'] = request.form.get("ail_key")

        print(input_dict)

        res = ail_2_ail.api_create_ail_instance(input_dict)
        if res[1] != 200:
            return create_json_response(res[0], res[1])

        return redirect(url_for('ail_2_ail_sync.ail_server_view', uuid=res))
    else:

        return render_template("add_ail_server.html")

@ail_2_ail_sync.route('/settings/ail_2_ail/server/edit', methods=['GET', 'POST'])
@login_required
@login_admin
def ail_server_edit():
    ail_uuid = request.args.get('ail_uuid')

@ail_2_ail_sync.route('/settings/ail_2_ail/server/delete', methods=['GET'])
@login_required
@login_admin
def ail_server_delete():
    ail_uuid = request.args.get('uuid')
    input_dict = {"uuid": ail_uuid}
    res = ail_2_ail.api_delete_ail_instance(input_dict)
    if res[1] != 200:
        return create_json_response(res[0], res[1])
    return redirect(url_for('ail_2_ail_sync.ail_servers'))

@ail_2_ail_sync.route('/settings/ail_2_ail/server/sync_queues', methods=['GET'])
@login_required
@login_admin
def ail_server_sync_queues():
    ail_uuid = request.args.get('uuid')
    sync_queues = ail_2_ail.get_all_unregistred_queue_by_ail_instance(ail_uuid)
    sync_queues = ail_2_ail.get_queues_metadata(sync_queues)

    return render_template("register_queue.html", bootstrap_label=bootstrap_label,
                                ail_uuid=ail_uuid, sync_queues=sync_queues)

@ail_2_ail_sync.route('/settings/ail_2_ail/server/sync_queues/register', methods=['GET'])
@login_required
@login_admin
def ail_server_sync_queues_register():

    ail_uuid = request.args.get('ail_uuid')
    queue_uuid = request.args.get('queue_uuid')
    input_dict = {"ail_uuid": ail_uuid, "queue_uuid": queue_uuid}
    res = ail_2_ail.api_register_ail_to_sync_queue(input_dict)
    if res[1] != 200:
        return create_json_response(res[0], res[1])
    return redirect(url_for('ail_2_ail_sync.ail_server_view', uuid=ail_uuid))

@ail_2_ail_sync.route('/settings/ail_2_ail/server/sync_queues/unregister', methods=['GET'])
@login_required
@login_admin
def ail_server_sync_queues_unregister():

    ail_uuid = request.args.get('ail_uuid')
    queue_uuid = request.args.get('queue_uuid')
    input_dict = {"ail_uuid": ail_uuid, "queue_uuid": queue_uuid}
    res = ail_2_ail.api_unregister_ail_to_sync_queue(input_dict)
    if res[1] != 200:
        return create_json_response(res[0], res[1])
    return redirect(url_for('ail_2_ail_sync.ail_server_view', uuid=ail_uuid))

####################
#                  #
#### SYNC QUEUE ####

@ail_2_ail_sync.route('/settings/ail_2_ail/sync_queues', methods=['GET'])
# @login_required
# @login_admin
def sync_queues():
    ail_uuid = request.args.get('ail_uuid')
    l_queues = ail_2_ail.get_all_queues_metadata()
    return render_template("sync_queues.html", bootstrap_label=bootstrap_label,
                                ail_uuid=ail_uuid, l_queues=l_queues)

@ail_2_ail_sync.route('/settings/ail_2_ail/sync_queue/view', methods=['GET'])
# @login_required
# @login_admin
def sync_queue_view():
    queue_uuid = request.args.get('uuid')
    queue_metadata = ail_2_ail.get_sync_queue_metadata(queue_uuid)
    ail_servers = ail_2_ail.get_sync_queue_all_ail_instance(queue_uuid)
    queue_metadata['ail_servers'] = ail_2_ail.get_ail_instances_metadata(ail_servers)
    return render_template("view_sync_queue.html", queue_metadata=queue_metadata,
                                bootstrap_label=bootstrap_label)

@ail_2_ail_sync.route('/settings/ail_2_ail/sync_queue/add', methods=['GET', 'POST'])
@login_required
@login_admin
def sync_queue_add():
    if request.method == 'POST':
        queue_name = request.form.get("queue_name")
        description = request.form.get("queue_description")
        max_size = request.form.get("queue_max_size")

        taxonomies_tags = request.form.get('taxonomies_tags')
        if taxonomies_tags:
            try:
                taxonomies_tags = json.loads(taxonomies_tags)
            except Exception:
                taxonomies_tags = []
        else:
            taxonomies_tags = []
        galaxies_tags = request.form.get('galaxies_tags')
        if galaxies_tags:
            try:
                galaxies_tags = json.loads(galaxies_tags)
            except Exception:
                galaxies_tags = []

        tags = taxonomies_tags + galaxies_tags
        input_dict = {"name": queue_name, "tags": tags,
                        "description": description,
                        "max_size": max_size}

        res = ail_2_ail.api_create_sync_queue(input_dict)
        if res[1] != 200:
            return create_json_response(res[0], res[1])

        return redirect(url_for('ail_2_ail_sync.sync_queue_view', uuid=res))
    else:
        return render_template("add_sync_queue.html", tags_selector_data=Tag.get_tags_selector_data())

@ail_2_ail_sync.route('/settings/ail_2_ail/sync_queue/edit', methods=['GET', 'POST'])
# @login_required
# @login_admin
def sync_queue_edit():
    return ''

@ail_2_ail_sync.route('/settings/ail_2_ail/sync_queue/delete', methods=['GET'])
# @login_required
# @login_admin
def sync_queue_delete():
    queue_uuid = request.args.get('uuid')
    input_dict = {"uuid": queue_uuid}
    res = ail_2_ail.api_delete_sync_queue(input_dict)
    if res[1] != 200:
        return create_json_response(res[0], res[1])
    return redirect(url_for('ail_2_ail_sync.sync_queues'))

#### JSON ####

##  - -  ##