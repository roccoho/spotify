import os
import requests 

class Discord():
    def __init__(self) -> None:  
        self.url = 'https://discord.com/api/v9/channels/{channel}/messages'    

        self.headers = {
            "Authorization": os.environ['DISCORD_TOKEN'], 
        } 

    
    def send_file(self, channel_id: str, filename: str, fileobj: bytes=None):  
        url = self.url.format(channel=channel_id) 

        if not fileobj: 
            filepath = filename
            filename = filepath.split('/')[-1]
            fileobj = open(filepath, 'rb')

        files = {
            'file[0]': (filename, fileobj)
        }   
 
        r = requests.post(url, 
                          headers=self.headers, 
                          files=files)   
        return r
    
    
    def get_file(self, channel_id: str, filepath: str):  
        url = self.url.format(channel=channel_id)  
        r = requests.get(url=url, 
                         headers=self.headers, 
                         params={'limit':1}) 
 
        dl_link = r.json()[0].get('attachments')[0].get('url')
        file = requests.get(dl_link)
        
        with open(filepath, 'wb') as f: 
            f.write(file.content)

        return file.content