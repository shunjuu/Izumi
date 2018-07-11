import os
import sys
import shutil

def get_dest_folder(original):
    """
    Original: /media/../.NyaaV2/[ReinForce] ...
    """
    og_path = original.split('/')
    new_path = str()

    for idx, folder in enumerate(og_path):
        if folder == ".NyaaV2":
            og_path[idx] = ".temp-rein"
        
    for folder in og_path:
        if folder:
            new_path = new_path + "/" + folder
    
    return new_path + "/"

def handle_raw(inotifywatch_str):
    """
    Example arg: /media/9da3/rocalyte/www/rocalyte.ananke/public_html/Public/.NyaaV2/,"CREATE,ISDIR",[ReinForce] Comic Girls - Vol 1 (BDRip...)
    """

    print("Raw arg: " + inotifywatch_str)

    # Simple safety check
    if "ISDIR" not in inotifywatch_str:
        print("The new file made was not a directory, returning...")
        sys.exit(0)

    args = inotifywatch_str.split(',')

    src_dir = args[0] + args[3]
    if len(args) > 3:
        for i in range(4, len(args)):
            src_dir = src_dir + "," + args[i]


    dest_dir = get_dest_folder(src_dir)

    print("src_dir: " + src_dir)
    print("dest_dir: " + dest_dir)

    print("Copying...")
    shutil.copytree(src_dir, dest_dir,symlinks=False)
    shutil.rmtree(src_dir)
    print()
    for dirpath,dirnames,fnames in os.walk(dest_dir):
#        print("dirpath: " + dirpath) 
#        print("dirnames: " + str(dirnames))
#        print("fnames: " + str(fnames))

        # Traverse through each dirpath and rename all files in there
        # Ignore any dirname, they will also show up in dirpath
        for name in fnames:
            if name.startswith("[ReinForce] "):
                print(name.replace("[ReinForce] ", ""))

                curr_file = dirpath + "/" + name
                new_file = dirpath + "/" + name.replace("[ReinForce] ", "")

                shutil.move(curr_file, new_file)

#        print()

    # Rename all the files
    new_dest_dir = dest_dir.replace("[ReinForce] ", "")
    shutil.move(dest_dir, new_dest_dir)

    # Call the sync script
    root_dir = os.getcwd() + "/"
    print("Syncing...")
    os.system(root_dir + "sync/raws.sh")
    
    # Delete the files
#    shutil.rmtree(new_dest_dir)
    os.system("rm -r " + '"' + new_dest_dir + '"')

    print("Done processing.")

    sys.exit(0)

if __name__ == "__main__":
    handle_raw(sys.argv[1])
