import json
import urllib.request
import subprocess
import socket

def ping_server(server_address):
    try:
        # Create a socket object
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)  # Set a timeout for the connection attempt

        # Attempt to connect to the server
        sock.connect((server_address, 80))  # Using port 80 as an example
        return True
    except Exception as e:
        print(f"Error: {e} : Execution_Node is down")
        return False

def lambda_handler(event, context):
    print(event)
    try:
        # Extract job_id from the event payload
        request_body = json.loads(event['body'])
        job_id = request_body['job_id']
        
        # Step 1: Make a GET request to check the job status
        get_url = f'http://3.144.43.175:32277/api/v2/jobs/{job_id}/'
        get_headers = {
            'Authorization': 'Bearer LP4KT5ZHnX29jaJzPKtZcpXxB7zyhu'
        }
        get_req = urllib.request.Request(get_url, headers=get_headers)
        
        with urllib.request.urlopen(get_req) as get_response:
            if get_response.getcode() == 200:
                job_data = json.loads(get_response.read().decode())
                
                # Step 2: Check if the job status is "failed"
                if job_data.get('status') == 'failed':

                    # Extract execution node IP address
                    #execution_node = job_data.get('job_env', {}).get('ELASTICSEARCH_MASTER_SERVICE_HOST')
                    execution_node = job_data.get('execution_node')
                    #execution_node = "3.144.43.175"
                    if execution_node:                    
                        # Step 3: Ping the execution node                                                
                        if not ping_server(execution_node):
                            # Ping failed, proceed to relaunch the job
                            relaunch_url = f'http://3.144.43.175:32277/api/v2/jobs/{job_id}/relaunch/'
                            relaunch_headers = {
                                'Authorization': 'Bearer LP4KT5ZHnX29jaJzPKtZcpXxB7zyhu'
                            }
                            relaunch_req = urllib.request.Request(relaunch_url, headers=relaunch_headers, method='POST')
                            
                            with urllib.request.urlopen(relaunch_req) as relaunch_response:
                                if relaunch_response.getcode() == 201:
                                    return {
                                        'statusCode': 201,
                                        'body': 'Job relaunched successfully'
                                    }
                                else:
                                    return {
                                        'statusCode': relaunch_response.getcode(),
                                        'body': 'Failed to relaunch job'
                                    }
                        else:
                            return {
                                'statusCode': 201,
                                'body': f'Server at {execution_node} is reachable'
                            }
                    else:
                        return {
                            'statusCode': 201,
                            'body': 'Execution node IP not found'
                        }                        
                else:
                    return {
                        'statusCode': 201,
                        'body': 'Job status is not failed'
                    }
            else:
                return {
                    'statusCode': get_response.getcode(),
                    'body': 'Failed to retrieve job data'
                }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': str(e)
        }
