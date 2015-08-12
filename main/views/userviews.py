import json
def getGravatar(email):
    base_src = "https://secure.gravatar.com/avatar/"
    email_md5 = ktk.md5(email) if email else "";
    return base_src + email_md5

def userAvatar(request, email):
    context = {}
    if email:
        context['headimg'] = getGravatar(email)
    else:
        return infoMsg("请输入email")
    return render_to_response('user/avatar.html', context)

def userUser(request):
    context = {}
    searchable_cols = ('username','id','email');
    try:
        for sc in searchable_cols:
            if sc in request.GET:
                kwargs = {sc : request.GET.get(sc)}
                user = User.objects.get(**kwargs);
                context['headimg'] = getGravatar(user.email);
                context['user'] = user
                return render_to_response('user/index.html', context);
        error_msg = "错误的参数：{0}\n".format(json.dumps(dict(request.GET)))
        error_msg += "请输入 {0} 中的一种".format(', '.join(searchable_cols))
        return infoMsg(error_msg, title='参数错误');
    except User.DoesNotExist:
        return infoMsg("用户 {0} 不存在".format(json.dumps(dict(request.GET))), title='参数错误')

def userLogin(request):
    context = {}
    username = request.POST.get('username')
    answer = request.POST.get('answer')
    if not username:
        return infoMsg("用户名不能为空", title="登陆失败")
    if not answer:
        return infoMsg("答案不能为空", title="登陆失败")
    if 'redirect' in request.GET:
        return redirect(request.GET.get('redirect'))
    else:
        return redirect('/')
