from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
from opcua import ua
from opcua import Client #para utilizar funciones OPC-UA
import json

import yaml   
with open("Configuration.yml") as fichero:
    conf=yaml.load(fichero)

#print(conf)
-+
print(conf['PLC']['IP'])
print(conf['PLC']['PORT'])
print(conf['PLC']['IP'])
print(conf['OPIL']['IP'])
print(conf['OPIL']['PORT'])
print('prueba para sourcetree')
    

client = Client("opc.tcp://192.168.250.1:4840") #empezar la sesion OPC-UA sabiendo la IP del servidor
client.connect()
#**************************************************************************
#*********************STATUS AND COMMANDS SIGNALS**************************
#**************************************************************************
#Signal Status from PLC of mobile Robot Omron
Status_LocationX = client.get_node("ns=4;s=Status_LocationX")#Direccion del nodo
Status_LocationY = client.get_node("ns=4;s=Status_LocationY")#Direccion del nodo
Status_LocationTheta = client.get_node("ns=4;s=Status_LocationTheta")#Direccion del nodo
Status_Status = client.get_node("ns=4;s=Status_Status")#Direccion del nodo
Status_Error = client.get_node("ns=4;s=Status_Error")#Direccion del nodo
#Signal Commands to PLC for mobile Robot Omron
Opil_AGV_X_Goal = client.get_node("ns=4;s=Opil_AGV_X_Goal")#Direccion del nodo
Opil_AGV_Y_Goal = client.get_node("ns=4;s=Opil_AGV_Y_Goal")#Direccion del nodo
Opil_AGV_Th_Goal = client.get_node("ns=4;s=Opil_AGV_Th_Goal")#Direccion del nodo
Opil_Action_AGV = client.get_node("ns=4;s=ns=4;s=Opil_Action_AGV")#Direccion del nodo
Opil_Cobot_Stop = client.get_node("ns=4;s=Opil_Cobot_Stop")#Direccion del nodo
Opil_Cobot_Load = client.get_node("ns=4;s=Opil_Cobot_Load")#Direccion del nodo
Opil_Cobot_Load_Piece = client.get_node("ns=4;s=Opil_Cobot_Load_Piece")#Direccion del nodo
Opil_AGV_Goto = client.get_node("ns=4;s=Opil_AGV_Goto")#Direccion del nodo
Opil_AGV_X_Goal_in = client.get_node("ns=4;s=Opil_AGV_X_Goal_in")#Direccion del nodo
Opil_AGV_Y_Goal_in = client.get_node("ns=4;s=Opil_AGV_Y_Goal_in")#Direccion del nodo

#OPIL_AGV_MotionCount = client.get_node("ns=4;s=OPIL_AGV_MotionCount")#Direccion del nodo


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(json.dumps({
            'method': self.command,
            'path': self.path=='/v2',
            'real_path': parsed_path.query,
                 'query': parsed_path.query,
            'request_version': self.request_version,
            'protocol_version': self.protocol_version
            
        }).encode())
        print(parsed_path.query)
        return
    
    
    def do_POST(self):
        #content_length = int(self.headers.getheader('content-length'))
        content_length = int(self.headers['Content-Length'])
        post_body = self.rfile.read(content_length)
        data = json.loads(post_body.decode('utf8'))
        print('Empiezo')
        print (data)

        
        
        for key in data['data'][0]:
            if key == 'cancel_order':
                cancel_value = data['data'][0]['cancel_order']['value']['task_id']['value']['description']['value']
                Opil_Cobot_Stop.set_value(ua.DataValue(ua.Variant(cancel_value, ua.VariantType.Int16)))
                if cancel_value:
                    Opil_Cobot_Load_Piece.set_value(ua.DataValue(ua.Variant(0, ua.VariantType.Int16)))
                    Opil_Cobot_Load.set_value(ua.DataValue(ua.Variant(0, ua.VariantType.Int16)))
                    
            elif key == 'action_assignment':
                if  data['data'][0]['action_assignment']['value']['robot_action']['value']['category']['value'] == 10:
                    action_Load =1
                    piece1 = 1
                    Opil_Cobot_Load_Piece.set_value(ua.DataValue(ua.Variant(piece1, ua.VariantType.Int16)))
                    Opil_Cobot_Load.set_value(ua.DataValue(ua.Variant(action_Load, ua.VariantType.Int16)))
                elif  data['data'][0]['action_assignment']['value']['robot_action']['value']['category']['value'] == 11:
                    action_Load =1
                    piece2 = 2
                    Opil_Cobot_Load_Piece.set_value(ua.DataValue(ua.Variant(piece2, ua.VariantType.Int16)))
                    Opil_Cobot_Load.set_value(ua.DataValue(ua.Variant(action_Load, ua.VariantType.Int16)))
                    
                    
            elif key == 'motion_assignment':
                
                Opil_AGV_Goto.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                
                
                x_value =  data['data'][0]['motion_assignment']['value']['point']['value']['x']['value']
                y_value =  data['data'][0]['motion_assignment']['value']['point']['value']['y']['value']
                th_value =  data['data'][0]['motion_assignment']['value']['point']['value']['theta']['value']
                print(x_value)
                print(f'el valor para X-Goal es:' )
                print(y_value*1000-1373)
                print('---------------------------------------')
                print(y_value)
                print('el valor para Y-Goal es:')
                print(5408-x_value*1000)
                print('---')
                print(th_value)
                Opil_AGV_X_Goal_in.set_value(ua.DataValue(ua.Variant(y_value*1000-1373, ua.VariantType.Float)))
                Opil_AGV_Y_Goal_in.set_value(ua.DataValue(ua.Variant(5408-x_value*1000, ua.VariantType.Float)))
                #Opil_AGV_Th_Goal.set_value(ua.DataValue(ua.Variant(th_value, ua.VariantType.Int16)))
                seq =  data['data'][0]['motion_assignment']['value']['sequence']['value']['sequence_number']['value']
                leng =  data['data'][0]['motion_assignment']['value']['sequence']['value']['length']['value']
                if seq==leng:
                    Opil_AGV_Goto.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                    Opil_AGV_Goto.set_value(ua.DataValue(ua.Variant(False, ua.VariantType.Boolean)))
                    Opil_AGV_Goto.set_value(ua.DataValue(ua.Variant(True, ua.VariantType.Boolean)))
                
                
                
                
                #OPIL_AGV_MotionCount.set_value(ua.DataValue(ua.Variant(OPIL_AGV_MotionCount.get_value()+1, ua.VariantType.Int16)))                    
        
        """
        print("esto es postbody")
        if data["data"][0]["id"] == "Mobile_Omron":
            print("Modifiying values on Mobile Omron entity...")
            
            value1 = data ["data"][0]["Command"]["value"]["coordenates"]["x"]["value"]
            value2 = data ["data"][0]["Command"]["value"]["coordenates"]["y"]["value"]
            value3 = data ["data"][0]["Command"]["value"]["coordenates"]["th"]["value"]
            value4 = data ["data"][0]["Command"]["value"]["action_cmd"]["cmd"]["value"]
            Opil_X_Goal.set_value(ua.DataValue(ua.Variant(value1, ua.VariantType.Int32)))
            Opil_Y_Goal.set_value(ua.DataValue(ua.Variant(value2, ua.VariantType.Int32)))
            Opil_Th_Goal.set_value(ua.DataValue(ua.Variant(value3, ua.VariantType.Int16)))
            Opil_Action_AGV.set_value(ua.DataValue(ua.Variant(value4, ua.VariantType.Int16)))           
            print("el valor de X comand es...")
            print(value1)
                        
        else:
            print("Apunta otro")
        #print(data["data"][0]["id"])
        
        print("fin es postbody")
       """ 
        """
        if post_body ["data"][0]["id"]=="Cobot_Omron":
            print ("Bien hecho")
        else:
            print("no es esto")
        print(post_body ["data"][0]["id"])
        """
        
        #print(data)
        #print(data['data']['axis1'])
        #value = data["temperature"]["value"]
        #robotSignal1 = client.get_node("ns=4;s=Robot_Signal_1")#Direccion del nod
        #robotSignal1.set_value(ua.DataValue(ua.Variant(value, ua.VariantType.Int16)))

        parsed_path = urlparse(self.path)
        self.send_response(200)
        self.end_headers()
        post_body1 = self.wfile.write(json.dumps({
            'method': self.command,
            'path': self.path=='/v2',
            'real_path': parsed_path.query,
            'query': parsed_path.query,
            'request_version': self.request_version,
            'protocol_version': self.protocol_version,
            'body': data
        
        }).encode())
    
        #print(post_body1)
        #infor=post_body1
          
        return

  
    
if __name__ == '__main__':
    
    try:     
        server = HTTPServer(('192.168.250.243', 8011), RequestHandler)
        print('Starting server at http://localhost:8011')
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C received, shutting down server')
        server.socket.close()


