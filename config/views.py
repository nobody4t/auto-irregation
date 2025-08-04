from django.shortcuts import render

def h5_view_index(request):
    return render(request, 'index.html')
    # if request.method == 'POST':
    #     username = request.POST['username']
    #     password = request.POST['password']

    #     try:
    #         if username == 'honeybee' and password == 'mfcxtd2024':
    #             return render(request, 'index.html')
    #         else:
    #             return render(request, 'login.html', {'error_message': '用户名或密码错误'})
    #     except:
    #         # 用户验证失败，返回登录页面并显示错误信息
    #         return render(request, 'login.html', {'error_message': '用户名或密码错误'})
    # else:
    #     return render(request, 'login.html')