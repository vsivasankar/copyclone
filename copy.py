import os
import time
import re
import sys
import signal

def handler(signum, frame):
     exit(130)

signal.signal(signal.SIGINT, handler)

rclone_path = ""   #enter rclone and fclone configs paths
fclone_path = ""

my_drives = {     #enter all your drives with ids
}
categories = {    #enter your folder ids for respective categories
    "TV": "",
    "movie": "",
    "anime": "",
    "other_stuff": "",
}
sub_tv = {
    "tv_remux": "",
    "tv_encode": "",
    "tv_encode_pack": ""
}
sub_tv_remux = {
    "tv_remux_single": "",
    "tv_remux_pack": "",
    "tv_remux_4k_single": "",
    "tv_remux_4k_pack": ""
}
sub_tv_encode = {
    "tv_encode": "",
    "tv_encode_4k": ""
}
sub_tv_encode_pack = {
    "tv_encode_pack": "",
    "tv_encode_pack_4k": ""
}
sub_movie = {
    "movie_encode": "",
    "movie_encode_pack": "",
    "movie_remux": "",
}
sub_movie_remux = {
    "movie_remux": "",
    "movie_remux_4k": "",
}
sub_movie_encode = {
    "movie_encode": "",
    "movie_encode_4k": ""
}
sub_movie_encode_pack = {
    "movie_encode_pack": "",
    "movie_encode_pack_4k": ""
}
dump = ""

tv = {**sub_tv_remux, **sub_tv_encode, **sub_tv_encode_pack}
movie = {**sub_movie_encode, **sub_movie_remux, **sub_movie_encode_pack}
tv_list = list(tv)
movie_list = list(movie)

def time_decorator(func):
    def wrapper(*args, **kwargs):
        t0 = time.time()
        func(*args, **kwargs)
        t1 = time.time()
        print(f"\n\ntime taken for script to run  - {t1-t0}\n\n")
    return wrapper

class Drive_id:
    def __init__(self, source=None, destination=None, new_folder=None, config=None, isFile=None, local=None):
        self.source = source
        self.destination = destination
        self.config = config
        self.isFile = isFile
        self.new_folder = new_folder
        self.local = local

    def create_folder(self):
        if self.config != "file" and self.local is None:
            while True:
                inp = input("Create a new folder in destination (y/n): ")
                if inp not in ["n", "y", "N", "Y"]:
                    print("invalid input")
                    continue
                elif inp in ["y", "Y"]:
                    self.new_folder = input("Enter new folder name: ")
                break

    def ready_copy(self):
        global path
        if(self.config == "fclone" or self.config == "rclone"):
            if(self.config == "fclone"):
                path = fclone_path
            else:
                path = rclone_path
            with open(path, "rt+") as file:
                regex = r"(root_folder_id = )(.+[^\n])"
                if(self.local is True):
                    dest = dump
                else:
                    dest = self.destination
                ids = [self.source, dest]
                content = file.read()
                pattern = re.compile(regex)
                match = pattern.findall(content)
                count = 0
                for item in match:
                    if count < 2:
                        content = re.sub(item[1], ids[count], content, 1)
                        count += 1
                file.seek(0)
                file.write(content)

        elif (self.config == "file"):
            path = rclone_path
            with open(path, "rt+") as file:
                regex = r"(root_folder_id = )(.+[^\n])"
                content = file.read()
                pattern = re.compile(regex)
                match = pattern.findall(content)
                if(self.local is True):
                    dest = dump
                else:
                    dest = self.destination
                content = re.sub(match[0][1], dest, content, 1)
                file.seek(0)
                file.write(content)

    @time_decorator
    def start_clone(self):
        if (self.config == "rclone"):
            if self.local is True:
                rc_list = [
                    'rclone --config=', path, ' copy temp: "',
                    self.destination,
                    '" -Pv --drive-chunk-size 64M --drive-pacer-min-sleep=10ms --drive-pacer-burst=5000 --exclude RARBG.txt --checkers=16 --transfers=8'
                ]
            else:
                rc_list = [
                    'rclone --config=', path, ' copy temp: temp2:"',
                    self.new_folder,
                    '" -Pv --drive-server-side-across-configs --exclude RARBG.txt --drive-pacer-min-sleep=10ms --drive-pacer-burst=5000 --checkers=32 --transfers=32'
                ]
            rc = "".join(filter(None, rc_list))
            print("\nStarting rclone folder\n")
            os.system(rc)

        elif (self.config == "file"):
            if self.local is True:
                file_list = [
                    'rclone --config=', path, ' backend copyid temp2: "',
                    self.source,
                    '" "',
                    self.destination,
                    '" -Pv --drive-chunk-size 64M --drive-pacer-min-sleep=10ms --drive-pacer-burst=5000']
            else:
                file_list = [
                    "rclone --config=", path, " backend copyid temp2: '",
                    self.source,
                    "' temp:",
                    " -Pv --drive-server-side-across-configs --drive-pacer-min-sleep=10ms --drive-pacer-burst=5000"]
            file_clone = "".join(filter(None, file_list))
            print("\nStarting rclone file\n")
            os.system(file_clone)

        elif (self.config == "fclone"):
            if self.local is True:
                fclone = [
                    'fclone --config=', path, ' copy temp: "', self.destination,
                    '" -Pv --stats-one-line --stats=8s --exclude RARBG.txt --drive-chunk-size 64M --ignore-existing --drive-keep-revision-forever --checkers=16 --transfers=8 --drive-pacer-min-sleep=10ms --drive-pacer-burst=5000']
            else:
                fclone = [
                    "fclone --config=", path, " copy temp: temp2:",
                    '"',
                    self.new_folder,
                    '" -Pv --stats-one-line --stats=8s --exclude RARBG.txt --ignore-existing --drive-server-side-across-configs --drive-keep-revision-forever --checkers=256 --transfers=256 --drive-pacer-min-sleep=10ms --drive-pacer-burst=5000']        
            fc = "".join(filter(None, fclone))
            print("\nStarting fclone folder\n")
            os.system(fc)

def get(n):
    while True:
        try:
            inp = int(input("\nSelect an option from above: "))
        except ValueError:
            continue
        except TypeError:
            print("Invalid Option")
            continue
        if inp not in range(1, n + 1):
            print("Invalid Option")
            continue
        elif inp in range(1, n + 1):
            return inp

def pri(dictionary):
    for i, k in enumerate(dictionary):
        print(f"{i+1}: {k}")

def rclone_select(source, isFile):
    print("\n")
    if(not isFile):
        print("1: Rclone\n2: Fclone\n3: File")
        inp_rc = get(3)
        if inp_rc == 1:
            drive_id.config = "rclone"
        elif inp_rc == 2:
            drive_id.config = "fclone"
    elif (isFile or inp_rc == 3):
        print("\n*** File selected ***\n")
        drive_id.config = "file"

def folder_id(string):
    while True:
        i = input(f"Enter {string} Folder id or Drive link: ")

        if len(i) == 33:
            return i

        elif(len(i) != 33):
            if("drive" in i):
                m = re.match(r"https:\/\/drive\.google\.com\/(uc\?id=|file\/d\/|drive\/folders\/|drive\/u\/0\/folders\/)([A-Za-z0-9-_]+)|$|[\/|\&|\?|\b|\n](view\?usp=sharing|export=download|usp=sharing)?", i)
                if(m is None or len(m.group(2)) != 33):
                    print("\n---- Enter proper Folder_id ----")
                    continue
                elif(len(m.group(2)) == 33):
                    if((i.find('file') != -1) or (i.find("export=download") != -1)):
                        drive_id.isFile = True
                    return m.group(2)
            elif(("/home" in i) or ("~" in i) or ("mnt" in i)):
                if i[-1] == "/":
                    return i
                else:
                    return i + "/"
            else:
                print("\n---- Enter proper folder id or link ----\n")

def dest():
    pri(categories)
    print("5: Dump Folder")
    print("6: Custom Folder id")
    print("7: Local download") 
    inp_cat = get(len(categories) + 3)
    if inp_cat == 1:
        print("\n")
        pri(tv)
        inp_tv = get(len(tv))
        if inp_tv == 1:
            return tv[tv_list[0]]
        elif inp_tv == 2:
            return tv[tv_list[1]]
        elif inp_tv == 3:
            return tv[tv_list[2]]
        elif inp_tv == 4:
            return tv[tv_list[3]]
        elif inp_tv == 5:
            return tv[tv_list[4]]
        elif inp_tv == 6:
            return tv[tv_list[5]]
        elif inp_tv == 7:
            return tv[tv_list[6]]
        elif inp_tv == 8:
            return tv[tv_list[7]]
    elif inp_cat == 2:
        print("\n")
        pri(movie_list)
        inp_movie = get(len(movie_list))
        if inp_movie == 1:
            return movie[movie_list[0]]
        elif inp_movie == 2:
            return movie[movie_list[1]]
        elif inp_movie == 3:
            return movie[movie_list[2]]
        elif inp_movie == 4:
            return movie[movie_list[3]]
        elif inp_movie == 5:
            return movie[movie_list[4]]
        elif inp_movie == 6:
            return movie[movie_list[5]]
        elif inp_movie == 7:
            return movie[movie_list[6]]
    elif inp_cat == 3:
        return categories["anime"]
    elif inp_cat == 4:
        return categories["other_stuff"]
    elif inp_cat == 5:
        return dump
    elif inp_cat == 6:
        return folder_id("Destination")
    elif inp_cat == 7:
        return folder_id("Local path or")

#Execution starts here

drive_id = Drive_id()

drive_id.source = folder_id("Source")
rclone_select(drive_id.source, drive_id.isFile)
drive_id.destination = dest()
drive_id.create_folder()
drive_id.ready_copy()
drive_id.start_clone()
