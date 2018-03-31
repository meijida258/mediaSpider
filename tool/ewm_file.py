import qrcode, PIL, os, datetime
qr = qrcode.QRCode(
    version=3,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
data = input()
qr.add_data(data)
img = qr.make_image(fit=True)
save_name = str(datetime.datetime.today()).split('.')[0]
save_name = save_name.replace(':', '-')
img.save("C:/Users/Administrator/Desktop/%s.png" %save_name)


# def file_name_deal(file_name): # 获得名字，返回地址
#     file_name = file_name.replace('test_agent_', '')
#     file_class = file_name.split('_')
#     # 组装地址
#     file_path = base_path
#     source_path = 'test_agent'
#     for i in file_class:
#         file_path = file_path + '/' + source_path + '_' +i
#         source_path = source_path + '_' + i
#     return file_path

# base_path = 'C:/Users/Administrator/Desktop/二维码'
#
# if not os.path.exists(base_path):
#     os.mkdir(base_path)
#
# with open('C:/Users/Administrator/Desktop/test_agents.csv') as fl:
#     content = fl.readlines()[1:]
# for each_line in content:
#     file_name = each_line.split(',')[0]
#     file_content = each_line.split(',')[-1].replace('\n', '')
#     file_path = file_name_deal(file_name)
#     if not os.path.exists(file_path):
#         os.mkdir(file_path)
#     img = qrcode.make(file_content)
#     img.save(file_path + '/' + file_name + '.png')
