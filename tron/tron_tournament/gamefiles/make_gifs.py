from glob import glob
import os, re, sys

"""
For next year: in tournament.py, let's just remove all 
spaces and punctuation from the bot names, because it 
creates headaches when running os.system
"""


def make_gif(botname):
    cmd_botname = botname.replace(" ", "\ ")
    files = glob("*" + botname + "*")
    folder_cmd = "mkdir %s" % cmd_botname
    os.system(folder_cmd)
    for fi in files:
        cmd_fi = fi.replace(" ", "\ ")
        pics_cmd = "java -jar vis.jar %s %s" % (cmd_fi, cmd_botname)
        os.system(pics_cmd)
        game_name = fi.split(".")[0]
        game_name = game_name.replace(" ", "\ ")
        os.chdir(botname)
        vid_cmd = (
            "ffmpeg -r 5 -f image2 -s 160x160 -start_number 0 -i %%d.png -vcodec libx264 -crf 25 -pix_fmt yuv420p %s.mp4"
            % game_name
        )
        os.system(vid_cmd)
        pics = glob("*.png")
        for pic in pics:
            rm_cmd = "rm %s" % pic
            os.system(rm_cmd)
        os.chdir("..")


def bot_names():
    # reads in all student's bots and maps names to bot functions
    # should add a TAbot if necessary to make numbers even
    botnames = []
    SL = student_list()
    sys.path.insert(0, "/gpfs/main/course/cs1410/grading/projects/Tron/submit-0")
    for student in SL:
        login = student.split("/")[-1]
        exec("from %s import bots" % login)
        student_bot = bots.TournamentBot()
        name = student_bot.BOT_NAME
        botnames.append(name)

    return botnames


def student_list():
    students = glob("../../grading/projects/Tron/submit-0/*")
    valid = []
    for student in students:
        f = open(student + "/bots.py")
        text = f.read()
        if re.search("TournamentBot", text):
            valid.append(student)

    return valid


if __name__ == "__main__":
    botnames = bot_names()
    for botname in botnames:
        make_gif(botname)
