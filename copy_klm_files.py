import os

PORTLAND_ZIPS = [97002, 97005, 97006, 97007, 97008, 97009, 97013, 97015, 97022, 97024, 97026, 97027, 97030, 97034, 97035, 97045, 97060, 97062, 97068, 97070, 97080, 97086, 97089, 97106, 97109, 97113, 97116, 97123, 97124, 97125, 97133, 97140, 97201, 97202, 97203, 97204, 97205, 97206, 97208, 97209, 97210, 97211, 97212, 97213, 97214, 97215, 97216, 97217, 97218, 97219, 97220, 97221, 97222, 97223, 97224, 97225, 97227, 97229, 97230, 97231, 97232, 97233, 97236, 97239, 97266, 97267, 97302, 97303, 97304, 97305, 97306, 97317, 97351, 97371, 97373, 97301, 98604, 98606, 98607, 98642, 98660, 98661, 98662, 98663, 98664, 98665, 98682, 98683, 98684, 98685, 98686]
SEATTLE_ZIPS = [98001, 98002, 98003, 98004, 98005, 98006, 98007, 98008, 98010, 98011, 98012, 98020, 98021, 98023, 98026, 98028, 98029, 98030, 98031, 98032, 98033, 98034, 98036, 98037, 98039, 98040, 98042, 98043, 98047, 98052, 98053, 98055, 98056, 98057, 98058, 98059, 98072, 98074, 98075, 98077, 98087, 98092, 98101, 98102, 98103, 98104, 98105, 98106, 98107, 98108, 98109, 98112, 98115, 98116, 98117, 98118, 98119, 98121, 98122, 98125, 98126, 98133, 98134, 98136, 98144, 98146, 98148, 98155, 98158, 98159, 98166, 98168, 98177, 98178, 98188, 98195, 98198, 98199, 98201, 98203, 98204, 98207, 98208, 98275, 98296, 98354, 98402, 98403, 98405, 98406, 98407, 98416, 98421, 98422, 98465, 98501]

HOME_PATH = os.path.expanduser('~') # in case sam runs this
ALL_FOLDER_PATH = os.path.join(HOME_PATH, "workspace/rynly/zipcode-kml/unpacked")
PORTLAND_FOLDER_PATH = os.path.join(HOME_PATH, "workspace/rynly/zipcode-kml/subset/portland")
SEATTLE_FOLDER_PATH = os.path.join(HOME_PATH, "workspace/rynly/zipcode-kml/subset/seattle")

def main():
    print "Checking folders"
    check_folders()

    print "Copying portland zips"
    copy_files(PORTLAND_ZIPS, PORTLAND_FOLDER_PATH)

    print "Copying seattle zips"
    copy_files(SEATTLE_ZIPS, SEATTLE_FOLDER_PATH)


def check_folders():
    if not os.path.isdir(ALL_FOLDER_PATH):
        print "ERROR: no folder found at {}".format(ALL_FOLDER_PATH)
        print "Make sure folder exists and contains all kml files"
        exit(1)

    folder_contents = os.listdir(ALL_FOLDER_PATH)
    if not folder_contents:
        print "ERROR: folder at {} is empty, expecting it to contain klm files".format(ALL_FOLDER_PATH)
        exit(1)

    for folder_path in [PORTLAND_FOLDER_PATH, SEATTLE_FOLDER_PATH]:
        if not os.path.isdir(folder_path):
            print "Folder {} doesn't exist, creating it".format(folder_path)
            os.makedirs(folder_path)

        folder_contents = os.listdir(folder_path)
        if folder_contents:
            print "ERROR: destination folder {} not empty".format(folder_path)
            print "Contents: {}".format(folder_contents)
            exit(1)

def copy_files(zipcodes, destination_folder_path):
    for zipcode in zipcodes:

        # some zip codes are in our full unpacked set I guess?
        if zipcode == 98159:
            print "Skipping {}".format(zipcode)
            continue

        filename = "zip{}.kml".format(zipcode)
        source_filepath = os.path.join(ALL_FOLDER_PATH, filename)
        # source_filepath = "{}/zip{}.kml".format(ALL_FOLDER_PATH, zipcode)
        exit_code = os.system("cp {} {}".format(source_filepath, destination_folder_path))
        if exit_code != 0:
            print "Fail"
            exit(exit_code)


if __name__ == "__main__":
    main()
