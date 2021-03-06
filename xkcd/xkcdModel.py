#! /usr/bin/python
#-*- coding: utf-8 -*-

import json
import random
from urllib2 import urlopen
from PySide.QtCore import Qt, QAbstractListModel, QModelIndex

from background import BackgroundServer, background

bgServer = BackgroundServer()
bgServer.start()

class XkcdModel(QAbstractListModel):

    def __init__(self, parent=None):
        QAbstractListModel.__init__(self, parent)
        self.setRoleNames({Qt.DisplayRole: 'titleText', Qt.ToolTipRole: 'altText', Qt.UserRole: 'comicUrl'})
        self._validRoles = [Qt.DisplayRole, Qt.ToolTipRole, Qt.UserRole]
        lastComicInfo = json.loads(urlopen('http://xkcd.com/info.0.json').read())
        if not lastComicInfo:
            raise IOError('Could not fetch XKCD comic.')
        self._lastComicId = lastComicInfo['num']
        self._cache = {lastComicInfo['num']: XkcdModel._filterComicInfos(lastComicInfo)}

    def rowCount(self, parent=None):
        if parent is None:
            parent = QModelIndex()

        return self._lastComicId

    @staticmethod
    def _filterComicInfos(fullComicInfo):
        return {Qt.DisplayRole: fullComicInfo['title'], Qt.UserRole: fullComicInfo['img'],
                     Qt.ToolTipRole: fullComicInfo['alt'] }

    def _translateComicId(self, comicId):
        return self._lastComicId - comicId

    @background(bgServer)
    def _fetchXkcdJsonComic(self, comicId, index):

        url = 'http://xkcd.com/%d/info.0.json' % (int(comicId))
        fullComicInfo = json.loads(urlopen(url).read())

        self._cache[fullComicInfo['num']] = XkcdModel._filterComicInfos(fullComicInfo)
        self.dataChanged.emit(index)

    def getRandomComicId(self):
        """
        return 4 # chosen by fair dice roll.
                 # guaranteed to be random.
        """
        return random.randint(1, self._lastComicId)

    def data(self, index, role=Qt.DisplayRole):
        if not role in self._validRoles and index > self._lastComicId:
            return None

        comicId = index.row()
        elif comicId in self._cache:
            return self._cache[comicId][role]

        else:
            self._fetchXkcdJsonComic(comicId, index)
            return ''
