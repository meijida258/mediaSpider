from Crypto.Cipher import AES
import base64

class ParamsGet:
    def __init__(self):
        self.first_param_comment = "{rid:\"\", offset:\"0\", total:\"true\", limit:\"20\", csrf_token:\"\"}"
        self.first_param_lyric = '{id: \"music_id\", lv: \"-1\", tv: \"-1\", csrf_token: \"\"}'
        self.second_param = '010001'
        self.third_param = '00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7'
        self.forth_param = '0CoJUm6Qyw8W8jud'


    def get_params(self, first_param, music_id=None):
        iv = '0102030405060708'
        first_key = self.forth_param
        second_key = 'F' * 16
        deal_first_param = first_param.replace('music_id', str(music_id))
        h_encText = self.AES_encrypt(deal_first_param, first_key, iv).decode('utf-8')
        h_encText = self.AES_encrypt(h_encText, second_key, iv).decode('utf-8')
        return h_encText


    def get_encSecKey(self):
        encSecKey = '257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c'
        return encSecKey


    def AES_encrypt(self, text, key, iv):
        pad = 16 - len(text) % 16
        text = text + pad * chr(pad)
        encryptor = AES.new(key, AES.MODE_CBC, iv)
        encrypt_text = encryptor.encrypt(text)
        encrypt_text = base64.b64encode(encrypt_text)
        return encrypt_text


    def get_params_data(self):
        params_data = {}
        params_data['params'] = self.get_params(self.first_param_comment)
        params_data['encSecKey'] = self.get_encSecKey()
        return params_data

if __name__ == '__main__':
    pg = ParamsGet()
else:
    pg = ParamsGet()