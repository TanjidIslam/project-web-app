import os
import traceback


def create_folder(foldername):
    # detect the current working directory and print it
    new_path = os.getcwd()
    print("The current working directory is %s" % new_path)

    try:
        exactpath = new_path + "/" + foldername
        if not os.path.isdir(exactpath):
            os.makedirs(exactpath)
            print("Successfully created:", exactpath)
    except OSError:
        print("Creation of the directory %s failed" % exactpath)
        print(traceback.print_exc())

def create_file(filename, directory, subdirectory, subdomain):
    create_folder(directory + '/' + subdomain + '/%s/' % subdirectory)
    save_path = os.getcwd()
    complete_name = os.path.join(save_path, '%s/%s/%s/%s' % (directory, subdomain, subdirectory, filename))
    return complete_name