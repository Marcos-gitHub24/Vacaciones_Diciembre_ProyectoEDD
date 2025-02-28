# B+ Mode Package
# Released under MIT License
# Copyright (c) 2020 TytusDb Team

import AVLTree
import BplusTree
import os
import pickle
import Serializable as serializable
import re
import shutil


def checkData():
    if not os.path.isdir("./Data"):
        os.mkdir("./Data")
    if not os.path.isfile("./Data/Databases.bin"):
        with open("./Data/Databases.bin", 'wb') as f:
            dataBaseTree = AVLTree.AVLTree()
            pickle.dump(dataBaseTree, f)


# Checks if the name is a valid SQL Identifier
def validateIdentifier(identifier):
    # Returns true if is valid
    try:
        return not re.search(r"[^a-zA-Z0-9_@#$]+|^[\s0-9@<>%$]", identifier)
    except:
        return False


def createDatabase(database):
    if type(database) !=str:
        return 1
    checkData()
    if database and validateIdentifier(database):
        dataBaseTree = serializable.Read('./Data/', 'Databases')
        root = dataBaseTree.getRoot()
        if dataBaseTree.search(root, database.upper()):
            return 2
        else:
            dataBaseTree.add(root, database.upper())
            serializable.write('./Data/', database, AVLTree.AVLTree())
            serializable.update('./Data/', 'Databases', dataBaseTree)
        return 0
    else:
        return 1


def showDatabases():
    checkData()
    dataBaseTree = serializable.Read('./Data/', "Databases")
    root = dataBaseTree.getRoot()
    dbKeys = dataBaseTree.postOrder(root)
    return [] if len(dbKeys) == 0 else dbKeys[:-1].split("-")


def alterDatabase(dataBaseOld, dataBaseNew) -> int:
    if type(dataBaseOld) !=str or type(dataBaseNew)!=str:
        return 1
    checkData()
    if validateIdentifier(dataBaseOld) and validateIdentifier(dataBaseNew):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, dataBaseOld.upper()):
            return 2
        if dataBaseTree.search(root, dataBaseNew.upper()):
            return 3
        dataBaseTree.delete(root, dataBaseOld.upper())
        serializable.Rename('./Data/', dataBaseOld, dataBaseNew)
        dataBaseTree.add(root, dataBaseNew.upper())
        serializable.update('./Data/', 'Databases', dataBaseTree)
        return 0
    else:
        return 1


def dropDatabase(database):
    if type(database) !=str:
        return 1
    checkData()
    if validateIdentifier(database):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return 2
        dataBaseTree.delete(root, database.upper())
        serializable.delete('./Data/' + database)
        serializable.update('./Data/', 'Databases', dataBaseTree)
        return 0
    else:
        return 1
    
# ---------------CRUD TABLE----------------#
# ----------------Erick--------------------#

def createTable(database, table, numberColumns):
    if type(database) !=str or type(table)!=str or type(numberColumns)!=int:
        return 1
    # Validates identifier before searching
    if validateIdentifier(database) and validateIdentifier(table) and numberColumns > 0:
        checkData()
        # Get the databases tree
        dataBaseTree = serializable.Read('./Data/', "Databases")
        # Get the dbNode
        databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
        # If DB exist
        if databaseNode:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if tablesTree.search(tablesTree.getRoot(), table.upper()):
                return 3
            else:
                # Creates new table node
                tablesTree.add(tablesTree.getRoot(), table.upper())
                serializable.update(f"./Data/{database}/", database, tablesTree)
                # Creates bin file for the new table
                serializable.write(f"./Data/{database}/", table, BplusTree.BPlusTree(5, numberColumns))
                return 0
        else:
            return 2
    else:
        return 1


def showTables(database):
    if type(database) !=str:
        return 1
    checkData()
    if validateIdentifier(database):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        if dataBaseTree.search(dataBaseTree.getRoot(), database.upper()):
            db = serializable.Read(f"./Data/{database}/", database)
            dbKeys = db.postOrder(db.getRoot())
            return [] if len(dbKeys) == 0 else dbKeys[:-1].split("-")
        else:
            return None
    else:
        return None


def extractTable(database, table):
    if type(database) !=str or type(table)!=str:
        return None
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        # Get the databases tree
        dataBaseTree = serializable.Read('./Data/', "Databases")
        # Get the dbNode
        databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
        # If DB exist
        if databaseNode:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if tablesTree.search(tablesTree.getRoot(), table.upper()):
                table = serializable.Read(f'./Data/{database}/{table}/', table)
                return list(table.lista().values())
            else:
                return None
        else:
            return None
    else:
        return None


def extractRangeTable(database, table, columnNumber, lower, upper):
    if type(database) !=str or type(table)!=str or type(columnNumber)!=int:
        return None
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        # Get the databases tree
        dataBaseTree = serializable.Read('./Data/', "Databases")
        # Get the dbNode
        databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
        # If DB exist
        if databaseNode:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if tablesTree.search(tablesTree.getRoot(), table.upper()):
                table = serializable.Read(f'./Data/{database}/{table}/', table)
                tableList = list(table.lista().values())
                validList = []

                if columnNumber < 0 or columnNumber >= table.columns:
                    return None
                try:
                    for i in tableList:
                        if type(i[columnNumber]) == str:
                            if str(i[columnNumber]) <= str(upper) and str(i[columnNumber]) >= str(lower):
                                validList.append(i)
                        elif type(i[columnNumber]) == float:
                            if float(i[columnNumber]) <= float(upper) and float(i[columnNumber]) >= float(lower):
                                validList.append(i)
                        elif type(i[columnNumber]) == int:
                            if int(i[columnNumber]) <= int(upper) and int(i[columnNumber]) >= int(lower):
                                validList.append(i)
                        elif type(i[columnNumber]) == bool:
                            if bool(i[columnNumber]) <= bool(upper) and bool(i[columnNumber]) >= bool(lower):
                                validList.append(i)
                except:
                    return None
                return validList

            else:
                return None
        else:
            return None
    else:
        return None


# ---------------Dyllan--------------------#

def alterAddPK(database: str, table: str, columns: list) -> int:
    try:
        if type(database)!=str or type(table)!=str or type(columns)!=list:
            return 1
        checkData()
        # Get the databases tree
        if validateIdentifier(database) and validateIdentifier(table):
            dataBaseTree = serializable.Read('./Data/', "Databases")
            # Get the dbNode
            databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
            # If DB exist
            if databaseNode:
                tablesTree = serializable.Read(f"./Data/{database}/", database)
                if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                    return 3  # table no existente
                else:
                    tuplaTree = serializable.Read(f"./Data/{database}/{table}/", table)
                    maximun = max(columns)
                    minimun = min(columns)
                    numberColumnsA = tuplaTree.columns  # actual amount from column
                    if not (minimun >= 0 and maximun < numberColumnsA):
                        return 5
                    try:
                        res = tuplaTree.CreatePK(columns)
                    except:
                        return 1
                    if res:
                        return res
                    else:
                        serializable.update(f"./Data/{database}/{table}/", table, tuplaTree)
                        return 0
            else:
                return 2  # database no 
        else:
            return 1
    except:
        return 1


def alterDropPK(database: str, table: str) -> int:
    try:
        if type(database)!=str or type(table)!=str:
            return 1
        checkData()
        if validateIdentifier(database) and validateIdentifier(table):
            dataBaseTree = serializable.Read('./Data/', "Databases")
            root = dataBaseTree.getRoot()
            if not dataBaseTree.search(root, database.upper()):
                return 2  # database no existente
            else:
                tablesTree = serializable.Read(f"./Data/{database}/", database)
                if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                    return 3  # table no existente

                PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
                res = PKsTree.DeletePk()
                if res:
                    return res
                else:
                    serializable.update(f'./Data/{database}/{table}/', table, PKsTree)
                return 0  # exito
        else:
            return 1
    except:
        return 1
# def alterAddFK(database: str, table: str, references: dict) -> int:
# def alterAddIndex(database: str, table: str, references: dict) -> int:  

 
def alterTable(database: str, tableOld: str, tableNew: str) -> int:
    if type(database) !=str or type(tableOld)!=str or type(tableNew)!=str:
        return 1
    checkData()
    if validateIdentifier(tableOld) and validateIdentifier(tableNew):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
        if databaseNode:
                tablesTree = serializable.Read(f"./Data/{database}/", database)
                rootT = tablesTree.getRoot()
                if not tablesTree.search(rootT, tableOld.upper()):
                    return 3 #tableOLD no existente
                elif tablesTree.search(rootT, tableNew.upper()):
                    return 4 #tableNEW existente
                
                tablesTree.delete(rootT, tableOld.upper())
                serializable.Rename(f'./Data/{database}/', tableOld, tableNew)
                tablesTree.add(rootT, tableNew.upper())
                serializable.update(f"./Data/{database}/", database, tablesTree)
                return 0
        else:
            return 2 #db no existente
    else:
        return 1
    
def alterAddColumn(database: str, table: str, default: any) -> int:   
    try:
        if type(database)!=str or type(table)!=str:
            return 1
        checkData()
        if validateIdentifier(database) and validateIdentifier(table):
            # Get the databases tree
            dataBaseTree = serializable.Read('./Data/', "Databases")
            # Get the dbNode
            databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
            # If DB exist
            if databaseNode:
                tablesTree = serializable.Read(f"./Data/{database}/", database)
                if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                    return 3  # table no existente
                else:
                    tuplaTree = serializable.Read(f"./Data/{database}/{table}/", table)
                    
                    res = tuplaTree.addColumn(default)
                    
                    if res:
                        return res
                    else:
                        serializable.update(f"./Data/{database}/{table}/", table, tuplaTree)
                        return 0
            else:
                return 2  # database no existente
        else:
            return 1
    except:
        return 1

def alterDropColumn(database: str, table: str, columnNumber: int) -> int:
    try:
        if type(database)!=str or type(table)!=str or type(columnNumber)!=int:
            return 1
        checkData()
        if validateIdentifier(database) and validateIdentifier(table):
            # Get the databases tree
            dataBaseTree = serializable.Read('./Data/', "Databases")
            # Get the dbNode
            databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
            # If DB exist
            if databaseNode:
                tablesTree = serializable.Read(f"./Data/{database}/", database)
                if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                    return 3  # table no existente
                else:
                    tuplaTree = serializable.Read(f"./Data/{database}/{table}/", table)
                    if columnNumber < 0 or columnNumber >= tuplaTree.columns:
                        return 5 #out of limit
                    else:
                        res = tuplaTree.dropColumn(columnNumber)
                        if res:
                            return res
                        else:
                            serializable.update(f"./Data/{database}/{table}/", table, tuplaTree)
                            return 0
            else:
                return 2  # database no existente
        else:
            return 1
    except:
        return 1

def dropTable(database: str, table: str) -> int:
    try:
        if type(database)!=str or type(table)!=str:
            return 1
        checkData()
        # Get the databases tree
        dataBaseTree = serializable.Read('./Data/', "Databases")
        databaseNode = dataBaseTree.search(dataBaseTree.getRoot(), database.upper())
        # If DB exist
        if databaseNode:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            root = tablesTree.getRoot()
            if not tablesTree.search(root, table.upper()):
                return 3 #table no existente
            else:
                tablesTree.delete(root, table.upper())
                serializable.delete(f"./Data/{database}/{table}")
                
                serializable.update(f"./Data/{database}/", database, tablesTree)
                return 0
        else:
            return 2
    except:
        return 1

# ---------------CRUD TUPLA----------------#
# ---------------Rudy----------------------#
def dropAll():
    if os.path.isdir('./Data'):
        shutil.rmtree('./Data')

def insert(database, table, register):
    if type(database) !=str or type(table)!=str or type(register)!=list:
        return 1
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return 2  # database no existente
        else:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                return 3  # table no existente
            PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
            res = PKsTree.register(register)
            if res:
                return res
            serializable.update(f'./Data/{database}/{table}/', table, PKsTree)
            return 0  # exito
    else:
        return 1

def loadCSV(filepath, database, table):
    if type(database) !=str or type(table)!=str or type(filepath)!=str:
        return []
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return []
        tablesTree = serializable.Read(f"./Data/{database}/", database)
        if not tablesTree.search(tablesTree.getRoot(), table.upper()):
            return []
        try:
            res = []
            import csv
            PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
            with open(filepath, 'r') as file:
                reader = csv.reader(file, delimiter=',')
                for row in reader:
                    res.append(PKsTree.register(row))
            serializable.update(f'./Data/{database}/{table}/', table, PKsTree)
            return res
        except:
            return []
    else:
        return []

def extractRow(database, table, columns):
    if type(database) !=str or type(table)!=str or type(columns)!=list:
        return []
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return []  # database no existente
        else:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                return []  # table no existente
            PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
            return PKsTree.search(columns)  # exito
    else:
        return []

def update(database, table, register, columns):
    if type(database) !=str or type(table)!=str or type(register)!=dict or type(columns)!=list:
        return 1
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return 2  # database no existente
        else:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                return 3  # table no existente
            PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
            try:
                res = PKsTree.update(register, columns)
                serializable.update(f'./Data/{database}/{table}/', table, PKsTree)
                return res
            except:
                return 1
    else:
        return 1

def delete(database, table, columns):
    if type(database) !=str or type(table)!=str or type(columns)!=list:
        return 1
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return 2  # database no existente
        else:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                return 3  # table no existente
            PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
            if len(PKsTree.search(columns)):
                try:
                    PKsTree.delete(columns)
                    serializable.update(f'./Data/{database}/{table}/', table, PKsTree)
                    return 0
                except:
                    return 1
            else:
                return 4
    else:
        return 1

def truncate(database, table):
    if type(database) !=str or type(table)!=str:
        return 1
    checkData()
    if validateIdentifier(database) and validateIdentifier(table):
        dataBaseTree = serializable.Read('./Data/', "Databases")
        root = dataBaseTree.getRoot()
        if not dataBaseTree.search(root, database.upper()):
            return 2  # database no existente
        else:
            tablesTree = serializable.Read(f"./Data/{database}/", database)
            if not tablesTree.search(tablesTree.getRoot(), table.upper()):
                return 3  # table no existente
            PKsTree = serializable.Read(f'./Data/{database}/{table}/', table)
            try:
                PKsTree.truncate()
                serializable.update(f'./Data/{database}/{table}/', table, PKsTree)
                return 0
            except:
                return 1
    else:
        return 1
    
def showCollection():
    checkData()
    dataB = showDatabases()
    print('DataBases: ',dataB)
    for x in dataB:
        print("")
        print("********************* [ DATABASE: "+str(x)+"] *********************")
        dataT = showTables(x)
        print(x,"Tables:",dataT)
        for y in dataT:
            print("")
            print("---------------------- [ TABLE: "+str(y)+"] ----------------------")
            dataTupla = extractTable(x, y)
            for z in dataTupla:
                print(z)

# ---------------Marcos--------------------#
