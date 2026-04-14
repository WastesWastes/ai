import streamlit
import os
from openai import OpenAI
from datetime import datetime
import json
from ollama import chat
from ollama import ChatResponse
import requests
import re

print("欢迎来到哈吉米")

#创建对话文件夹
if not os.path.exists("对话"):                         #判断对话文件夹是否存在
    os.mkdir("对话")

#gpt_sovits调用
def tts(texts: str = "旅行者,有什么事情吗？来听听我新创的歌吧"):
    """
    生成语音
    :param texts: 要生成的文本
    :return:二进制数值 get_tts.content
    """
    url = "http://127.0.0.1:9880/"
    refer_wav_path = r"C:\Users\MrWu\Downloads\温迪.wav"
    prompt_text = "骑士团代理团长大人？你觉得他是个怎样的人"
    prompt_language = "中文"
    text = texts
    text_language = "中文"
    top_k = "15"
    top_p = "1"
    temperature = "0.8"
    speed = "1"
    sample_steps = "32"
    if_sr = "false"
    urls = (url
            + "?refer_wav_path=" + refer_wav_path
            + "&prompt_text=" + prompt_text
            + "&prompt_language=" + prompt_language
            + "&text=" + text
            + "&text_language=" + text_language
            + "&top_k=" + top_k
            + "&top_p=" + top_p
            + "&temperature=" + temperature
            + "&speed=" + speed
            + "&sample_steps=" + sample_steps
            + "&if_sr=" + if_sr)
    try:
        get_tts = requests.get(urls)
        if get_tts.status_code == 200:
            print("生成成功")
            return get_tts.content
    except Exception as e:
        print("生成失败:", e)

def create_wav(get_tts,wav_name: str = "hajimi"):
    """
    保存为wav文件
    :param get_tts: 二进制数值
    :param wav_name: 文件名
    :return:
    """
    with open(f"../wav/{wav_name}.wav", "wb") as wav_save:
        wav_save.write(get_tts)
    print("保存成功")
# 去除括号中的文字
def remove_brackets(text: str):
    """
    去除括号中的文字
    :param text: 文本
    :return: 处理好的文本
    """
    # 多次循环处理嵌套括号，直到没有括号为止
    # 去除中文括号及其内容
    while '（' in text and '）' in text:
        new_text = re.sub(r'（[^）]*）', '', text)
        if new_text == text:
            break
        text = new_text
    # 去除英文括号及其内容
    while '(' in text and ')' in text:
        new_text = re.sub(r'\([^)]*\)', '', text)
        if new_text == text:
            break
        text = new_text
    # 清理剩余的不匹配括号
    text = text.replace(')', '').replace('(', '').replace('）', '').replace('（', '')
    return text

#加载会话列表函数
def load_dialogue_list():
    dialogue_list = []

    if os.path.exists("对话"):
        file_list = os.listdir("对话")
        for file in file_list:
            dialogue_date_name = ""
            with open(f"对话/{file}", 'r', encoding='utf-8') as dialogue:
                dialogue_py = json.load(dialogue)         #json 读取
                # 添加日期名字
                dialogue_date_name += dialogue_py["nowtime"]
                dialogue_date_name += dialogue_py["name"]
                dialogue_list.append(dialogue_date_name)
    #按日期排序
    dialogue_list.sort(reverse=True)
    #去掉日期
    dialogue_list_end = [i[19:] for i in dialogue_list]
    return dialogue_list_end

#加载对话列表
dialogues = load_dialogue_list()

#加载历史会话
def load_dialogue(file_name):
    """
    加载历史会话
    :param file_name: 文件名
    :return：
    """
    try:
        with open(f"对话/{file_name}.json", 'r', encoding='utf-8') as js:
            all_contents = json.load(js)
            print("load succeed")
            return all_contents

    except FileNotFoundError:
        print("file not found")

#页面设置
streamlit.set_page_config(
    page_title="哈吉米",
    page_icon="😽",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
    }
)

#logo
streamlit.logo(r"C:\Users\MrWu\Pictures\Camera Roll\b_d1bcbdd3b9e24ce17c177ea341ab5fb2.jpg")

#初始化系统设定
all_content = {}
if "system_name" not in streamlit.session_state:
    streamlit.session_state.system_name = "哈吉米"
if "system_text" not in streamlit.session_state:
    streamlit.session_state.system_text = "你叫哈吉米，只会喵喵叫"
if "content_store" not in streamlit.session_state or streamlit.session_state.content_store == []:
    streamlit.session_state.content_store = []
    streamlit.session_state.content_store.append({"role": "system", "content": f"你是{streamlit.session_state.system_name}，{streamlit.session_state.system_text}"})

#大标题
if streamlit.session_state.system_name:
    streamlit.header(f"{streamlit.session_state.system_name}")
else:
    streamlit.header("哈吉米")

#侧边栏
with streamlit.sidebar:
    streamlit.subheader("对话管理")
    #初始化思考模式
    if "chat_mode" not in streamlit.session_state:
        streamlit.session_state.chat_mode = "deepseek-chat"
    page_left, page_right = streamlit.columns([1, 1])
    #初始模型
    if "model" not in streamlit.session_state:
        streamlit.session_state.model = "online"              #定义session_state.model
    with page_left:
        # 切换线上模型
        if streamlit.button("线上模型",width="stretch",type="primary" if streamlit.session_state.model == "online" else "secondary"):
            streamlit.session_state.model = "online"
            streamlit.rerun ()
        # 切换思考
        if streamlit.button("对话模式", key="chat_thinking",width="stretch",type="primary" if streamlit.session_state.chat_mode == "deepseek-chat" else "secondary"):
            streamlit.session_state.chat_mode = "deepseek-chat"
            print("chat_mode:",streamlit.session_state.chat_mode)
            streamlit.rerun ()
    with page_right:
        # 切换本地模型
        if streamlit.button("本地模型",width="stretch",type="primary" if streamlit.session_state.model == "local" else "secondary"):
            streamlit.session_state.model = "local"
            streamlit.rerun ()
        # 切换思考
        if streamlit.button("思考模式", key="thinking",width="stretch",type="primary" if streamlit.session_state.chat_mode == "deepseek-reasoner" else "secondary"):
            streamlit.session_state.chat_mode = "deepseek-reasoner"
            print("chat_mode:",streamlit.session_state.chat_mode)
            streamlit.rerun ()
    button_new_dialogue = streamlit.button("新建对话", icon="😽",width="stretch") #新建对话
    button_save = streamlit.button("保存对话", icon="💾",width="stretch")          #保存对话

    system_name = streamlit.text_input("请输入哈吉米昵称",placeholder="哈吉米")         #昵称
    system_text = streamlit.text_area("请定义哈吉米",placeholder="请你叫哈吉米，只会喵喵叫", height=200)      #描述ai设定
    #显示对话列表
    streamlit.subheader("对话列表")
    page_side1, page_side2 = streamlit.columns([2, 1])
    for dialogue in dialogues:
        with page_side1:                                                                                        #判断是否是当前会话
            if streamlit.button(f"{dialogue}", icon="❤️", width="stretch", key=f"load_{dialogue}",type="primary" if dialogue == streamlit.session_state.system_name else "secondary"):
                try:
                    all_content = load_dialogue(dialogue)
                    streamlit.session_state.system_name = all_content["name"]
                    streamlit.session_state.system_text = all_content["text"]
                    streamlit.session_state.content_store = all_content["content"]
                    streamlit.success("加载成功")
                    streamlit.rerun()
                except Exception as e:
                    print(e)
                    streamlit.error("加载失败")

        with page_side2:
            if streamlit.button("删除", width="stretch", key=f"delete_{dialogue}"):
                try:
                    os.remove(f"对话/{dialogue}.json")
                    if dialogue == streamlit.session_state.system_name:
                        streamlit.session_state.clear()
                        streamlit.rerun()
                    streamlit.success("删除成功")
                    streamlit.rerun()
                except Exception as e:
                    print(e)
                    streamlit.error("删除失败")
                pass


#修改系统设定
if system_name:
     streamlit.session_state.system_name = system_name
     streamlit.session_state.content_store[0]["content"] = f"你是{streamlit.session_state.system_name}，{streamlit.session_state.system_text}"#设定修改
if system_text:
    streamlit.session_state.system_text = system_text
    streamlit.session_state.content_store[0]["content"] = f"你是{streamlit.session_state.system_name}，{streamlit.session_state.system_text}"#修改ai设定

#初始化聊天对话
if "content_store" not in streamlit.session_state:
    streamlit.session_state.content_store = []
    streamlit.session_state.content_store.append({"role": "system", "content": f"你是{streamlit.session_state.system_name}，{streamlit.session_state.system_text}"})
print(streamlit.session_state.content_store)

#历史对话展示
for message in streamlit.session_state.content_store:
    streamlit.chat_message(message["role"]).write(message["content"])

#聊天输入框
content_user = streamlit.chat_input("请输入哈吉米")
#线上模型
if streamlit.session_state.model == "online":
    if content_user:                   #字符串自动转化为bool
        streamlit.chat_message("user").write(content_user) #显示网页用户对话
        streamlit.session_state.content_store.append({"role": "user", "content": content_user})#存储用户对话
        print("user content:",content_user) #输出用户输入
        #ai对话
        client = OpenAI(
            api_key=os.environ.get('DEEPSEEK_API_KEY'),
            base_url="https://api.deepseek.com")
        response = client.chat.completions.create(
            model=streamlit.session_state.chat_mode,
            messages=streamlit.session_state.content_store,
            stream=True
        )

        #流式对话
        response_area = streamlit.empty()
        response_area.write("正在思考...")
        full_response = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                content_assistant_stream = chunk.choices[0].delta.content
                full_response = full_response + content_assistant_stream
                response_area.chat_message("assistant").write(full_response) #显示网页ai对话

        #进行tts生成

        #if streamlit.button("播放音频", width="content"):
        #    print("000a")
        #    two_tts = tts(full_response)
        #    create_wav(two_tts,full_response[:6])
        #    streamlit.audio(f"../wav/{full_response[:6]}.wav")      #播放音频
        #    print("tts succeed")
        print(remove_brackets(full_response))
        two_tts = tts(remove_brackets(full_response))
        create_wav(two_tts,"hajimi")
        streamlit.audio(f"../wav/hajimi.wav")      #播放音频
        print("tts succeed")

        # 存储新对话
        streamlit.session_state.content_store.append({"role": "assistant", "content": full_response})
        print(streamlit.session_state.content_store)
#本地模型
if streamlit.session_state.model == "local":
    try:
        if content_user:
            streamlit.chat_message("user").write(content_user)   #显示网页用户对话
            streamlit.session_state.content_store.append({"role": "user", "content": content_user}) #存储用户对话
            print("user content:",content_user)
            #ai对话
            local_response: ChatResponse = chat(
                model='deepseek-r1:8b',
                messages=streamlit.session_state.content_store,
                stream=True
            )
            #流式对话
            response_area = streamlit.empty()
            response_area.write("正在思考...")
            full_response = ""
            for chunk in local_response:
                if chunk.message.content:
                    content_assistant_stream = chunk.message.content
                    full_response = full_response + content_assistant_stream   #累加对话
                    response_area.chat_message("assistant").write(full_response)
            # 存储新对话
            streamlit.session_state.content_store.append({"role": "assistant", "content": full_response})
            print(streamlit.session_state.content_store)
    except Exception as e:
        print(e)
        streamlit.error("请检查本地模型是否正常")
        streamlit.rerun()
#存储对话
all_content = {"nowtime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
               "name":streamlit.session_state.system_name,
               "text": streamlit.session_state.system_text,
               "content": streamlit.session_state.content_store}
print(all_content)

#新建对话
if button_new_dialogue:
    streamlit.session_state.clear()
    streamlit.rerun()
#保存对话
if button_save:
        with open(f"对话/{streamlit.session_state.system_name}.json", 'w', encoding='utf-8') as f:
            json.dump(all_content, f, ensure_ascii=False, indent=4)
            streamlit.success("保存成功")
            print("succeed save")
        streamlit.rerun()














