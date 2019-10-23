import os

ANALYSIS_FOLDER = os.path.abspath("/Users/mirek/Desktop/rynly_job_analysis")

# found packages with multiple pickup jobs (listed by both number and id) , igore the first one
# {'c6764abf-4805-427d-9cef-640fe3709333': ['3412', '3399'],'4c1d7752-445f-472e-9dc5-3728d59f7ec6': ['229', '228'], '9281c1a4-976e-4a10-b30b-016b53f79dce': ['156', '150'], '4349a36f-179c-4683-8866-b0a1de82124c': ['3228', '3226'], '24c43dcc-bdaa-49ea-968d-a1ead28d9266': ['1508', '1511']}
# {'c6764abf-4805-427d-9cef-640fe3709333': ['d821f6ab-b20e-4f99-aed4-b7f2f3448750', 'e1126c4f-89f5-488d-827f-0190d2a723b8'], '4c1d7752-445f-472e-9dc5-3728d59f7ec6': ['8ad32838-72c4-497c-a5d9-1a1afeed7c74', '5175468d-1d0c-46fa-813d-d6adb1ca65e9'], '9281c1a4-976e-4a10-b30b-016b53f79dce': ['8406f511-175a-4b63-a946-87561f358aa7', 'b4668184-56ee-488f-9924-b21e5e7740d4'], '4349a36f-179c-4683-8866-b0a1de82124c': ['3b1c37f4-7711-4b48-865d-fde4ae3d6c61', '0622f8f2-a97a-4e10-84c6-a29f9f555398'], '24c43dcc-bdaa-49ea-968d-a1ead28d9266': ['96b04795-99b8-48dd-b6ed-dbe7a3b0cd95', 'a96cebcf-d00b-4fee-83c9-92febe51624c']}
JOB_IDS_TO_IGNORE = set(["d821f6ab-b20e-4f99-aed4-b7f2f3448750", "8ad32838-72c4-497c-a5d9-1a1afeed7c74", "8406f511-175a-4b63-a946-87561f358aa7", "3b1c37f4-7711-4b48-865d-fde4ae3d6c61", "96b04795-99b8-48dd-b6ed-dbe7a3b0cd95"])

ONE_OFF_PACKAGES_TO_IGNORE = set([
    "bdb0482a-724f-414f-9a81-2228ff4aa206", # no pickup job, doesn't look admin-managed or anything tho
    # these have no delivery job, even though they generally DO have pickup jobs
    '7a66f2cf-7c60-4ce2-a3c4-08ebe92d3726', '4d91423d-ac7e-4f5d-9a87-381f49064cce', '68adaa32-ac5c-4b48-b9da-0bf70a0f6ccf', '529aba8f-d594-4c63-9268-ab9193b62bce', 'c605bbd6-2eca-4a21-a811-46a977990bea', '15548c54-079d-4cc6-9492-969faf47b3b9', '74473aa6-0474-4c6d-b046-621b51eee51a', '44a7a17d-6b87-4b32-8e13-b14cd5db0231', '625c348b-931d-410f-bf63-b88258d23322'
    ])


def get_bad_package_ids():
    return ONE_OFF_PACKAGES_TO_IGNORE.union(get_only_created_packages().union(get_only_created_and_delivered_packages()))


# input file format:
# _id,TrackingNumber,DateCreated,AmountPaid,JobId,IsExpedited,CancellationNote
def get_canceled_packages_set():
    cancelled_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "cancelled", "prod_cancelled_packages.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            cancelled_packages.add(_id)

    return cancelled_packages


# input file format:
# _id,Changes.0.Text,Changes.0.AdminChange,Changes.1.Text,Changes.1.AdminChange,Changes.2.Text,Changes.2.AdminChange,Changes.3.Text,Changes.3.AdminChange,Changes.4.Text,Changes.4.AdminChange,Changes.5.Text,Changes.5.AdminChange,Changes.6.Text,Changes.6.AdminChange,Changes.7.Text,Changes.7.AdminChangeChanges.8.Text,Changes.8.AdminChange,Changes.9.Text,Changes.9.AdminChange
def get_hub_dropoff_packages():
    hub_dropoff_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            change_1 = line.split(",")[1]
            change_2 = line.split(",")[3]
            if change_1 == "Package Created" and change_2 == "Package Checked In":
                hub_dropoff_packages.add(_id)

    return hub_dropoff_packages


def get_admin_checked_in_packages():
    admin_checked_in_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            change_2 = line.split(",")[3]
            change_2_is_admin = line.split(",")[4]
            if change_2 == "Package Picked By Driver" and change_2_is_admin == "true":
                admin_checked_in_packages.add(_id)

    # these jobs were created before we started tracking whether something was an admin change
    probably_admin_changes = ['859e7186-df59-4d29-afb9-026d34c9017f', '91508023-af37-46a8-a7cf-8e9ef27206db', 'b27ac951-3722-4909-876f-eb67a0d63b09', 'ab32a69b-8401-4928-a000-05374355621b', '9907ae2a-919e-4f85-93b5-7265dcf38c5a']
    admin_checked_in_packages.update(probably_admin_changes)

    return admin_checked_in_packages


# where last package update was "package delivered" and "admin change" is true
def get_admin_delivered_packages():
    admin_delivered_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        header_line = f.readline()
        max_changes = int(header_line.split(".")[-2]) # user header to determine number of "changes" columns

        if header_line.split(",")[-1] != "Changes.{}.AdminChange\n".format(max_changes):
            raise Exception("Header format logic wrong")

        for line in f.read().splitlines():
            _id = line.split(",")[0]

            # find last package delivered change
            change_N_text = None
            change_N_is_admin = None
            for i in range(max_changes, -1, -1): # e.g. 9,8,...,0
                text_index = 2 * i + 1
                is_admin_index = 2 * i + 2

                change_N_text = line.split(",")[text_index]
                change_N_is_admin = line.split(",")[is_admin_index]

                if change_N_text == "Package Delivered":
                    break

            if not change_N_text:
                raise Exception("Package never got delivered?")

            if change_N_is_admin == "true":
                admin_delivered_packages.add(_id)

    return admin_delivered_packages


# this is bad data, these packages have pikup jobs but no delivery jobs
def get_only_created_packages():
    only_created_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            change_1 = line.split(",")[1]
            change_2 = line.split(",")[3]
            if change_1 == "Package Created" and change_2 == "":
                only_created_packages.add(_id)

    return only_created_packages


# as above, this seems to be just bad data, pre-admin change logic (well, 2 have admin change data)
def get_only_created_and_delivered_packages():
    only_created_and_delivered_packages = set()
    with open(os.path.join(ANALYSIS_FOLDER, "package_changes", "package_changes.csv")) as f:
        for line in f.read().splitlines()[1:]: # skip header
            _id = line.split(",")[0]
            change_1 = line.split(",")[1]
            change_2 = line.split(",")[3]
            change_3 = line.split(",")[5]
            if change_1 == "Package Created" and change_2 == "Package Delivered" and change_3 == "":
                only_created_and_delivered_packages.add(_id)

    return only_created_and_delivered_packages
