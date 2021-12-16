# pip install packaes if not installed. e.g: open up cmd prompt and type "pip install tableauserverclient"

import getpass
import tableauserverclient as TSC

server_name = "https://10ax.online.tableau.com/"
user_name = "NYTableauDev@gmail.com"
password = "NDJNeSf5zLNt"  # getpass.getpass() #use getpass() method in production
# An empty string can used to specify the default site.
site_url_id = "mysitedev384565"#"nikuldev423951"
projectName = "Finance"
# WorkbookName = "Superstore" #uncomment this and provide a specific workbook name to narrow down the list

tableau_auth = TSC.TableauAuth(user_name, password, site_url_id)
server = TSC.Server(server_name)

with server.auth.sign_in(tableau_auth):

    all_workbooks_items, pagination_item = server.workbooks.get()
    for wb in TSC.Pager(server.workbooks):
        wbID = wb.id
        if wb.project_name == projectName:  # and wb.name == WorkbookName : #use with line#10. uncomment if list needs to be narrowed down to a specific workbook
            workbook = server.workbooks.get_by_id(wbID)
            server.workbooks.populate_views(workbook)
            print(workbook.project_name)
            print("\t", workbook.name)
            for view in workbook.views:
                print("\t", "\t", view.name + ": " + view.id)
