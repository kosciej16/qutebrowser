# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2014-2020 Florian Bruhin (The Compiler) <mail@qutebrowser.org>
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Functions that return miscellaneous completion models."""

import typing

from qutebrowser.config import config, configdata
from qutebrowser.utils import objreg, log
from qutebrowser.completion.models import completionmodel, listcategory, util
from qutebrowser.config import configdata
from qutebrowser.utils import log, objreg, tabutils


def command(*, info):
    """A CompletionModel filled with non-hidden commands and descriptions."""
    model = completionmodel.CompletionModel(column_widths=(20, 60, 20))
    cmdlist = util.get_cmd_completions(info, include_aliases=True,
                                       include_hidden=False)
    model.add_category(listcategory.ListCategory("Commands", cmdlist))
    return model


def helptopic(*, info):
    """A CompletionModel filled with help topics."""
    model = completionmodel.CompletionModel()

    cmdlist = util.get_cmd_completions(info, include_aliases=False,
                                       include_hidden=True, prefix=':')
    settings = ((opt.name, opt.description)
                for opt in configdata.DATA.values())

    model.add_category(listcategory.ListCategory("Commands", cmdlist))
    model.add_category(listcategory.ListCategory("Settings", settings))
    return model


def quickmark(*, info=None):  # pylint: disable=unused-argument
    """A CompletionModel filled with all quickmarks."""
    def delete(data: typing.Sequence[str]) -> None:
        """Delete a quickmark from the completion menu."""
        name = data[0]
        quickmark_manager = objreg.get('quickmark-manager')
        log.completion.debug('Deleting quickmark {}'.format(name))
        quickmark_manager.delete(name)

    model = completionmodel.CompletionModel(column_widths=(30, 70, 0))
    marks = objreg.get('quickmark-manager').marks.items()
    model.add_category(listcategory.ListCategory('Quickmarks', marks,
                                                 delete_func=delete,
                                                 sort=False))
    return model


def bookmark(*, info=None):  # pylint: disable=unused-argument
    """A CompletionModel filled with all bookmarks."""
    def delete(data: typing.Sequence[str]) -> None:
        """Delete a bookmark from the completion menu."""
        urlstr = data[0]
        log.completion.debug('Deleting bookmark {}'.format(urlstr))
        bookmark_manager = objreg.get('bookmark-manager')
        bookmark_manager.delete(urlstr)

    model = completionmodel.CompletionModel(column_widths=(30, 70, 0))
    marks = objreg.get('bookmark-manager').marks.items()
    model.add_category(listcategory.ListCategory('Bookmarks', marks,
                                                 delete_func=delete,
                                                 sort=False))
    return model


def session(*, info=None):  # pylint: disable=unused-argument
    """A CompletionModel filled with session names."""
    from qutebrowser.misc import sessions
    model = completionmodel.CompletionModel()
    try:
        sess = ((name,) for name
                in sessions.session_manager.list_sessions()
                if not name.startswith('_'))
        model.add_category(listcategory.ListCategory("Sessions", sess))
    except OSError:
        log.completion.exception("Failed to list sessions!")
    return model


#  def _buffer(skip_win_id=None):
#      """Helper to get the completion model for buffer/other_buffer.
#
#      Args:
#          skip_win_id: The id of the window to skip, or None to include all.
#      """
#      model = completionmodel.CompletionModel(column_widths=(6, 40, 54))
#
#  <<<<<<< HEAD
#      tabs_are_windows = config.val.tabs.tabs_are_windows
#      # list storing all single-tabbed windows when tabs_are_windows
#      windows = []  # type: typing.List[typing.Tuple[str, str, str]]
#
#      for win_id in objreg.window_registry:
#          if skip_win_id is not None and win_id == skip_win_id:
#              continue
#          tabbed_browser = objreg.get('tabbed-browser', scope='window',
#                                      window=win_id)
#          if tabbed_browser.shutting_down:
#              continue
#          tabs = []  # type: typing.List[typing.Tuple[str, str, str]]
#          for idx in range(tabbed_browser.widget.count()):
#              tab = tabbed_browser.widget.widget(idx)
#              tabs.append(("{}/{}".format(win_id, idx + 1),
#                           tab.url().toDisplayString(),
#                           tabbed_browser.widget.page_title(idx)))
#          if tabs_are_windows:
#              windows += tabs
#          else:
#              cat = listcategory.ListCategory(
#                  str(win_id), tabs, delete_func=delete_buffer, sort=False)
#              model.add_category(cat)
#
#      if tabs_are_windows:
#          win = listcategory.ListCategory(
#              "Windows", windows, delete_func=delete_buffer, sort=False)
#          model.add_category(win)
#  =======
#      for win_id, tabs in tabutils.all_tabs_by_window(skip_win_id).items():
#          f_tab = (("{}/{}".format(t.win_id, i + 1), t.url().toDisplayString(),
#                    t.title()) for i, t in enumerate(tabs))
#          cat = listcategory.ListCategory(
#              str(win_id), f_tab, delete_func=tabutils.delete_tab(0), sort=False)
#          model.add_category(cat)
#  >>>>>>> 72b6d52d806df3ae8e2599ed6f91d86f02c9c02f
#
#      return model


def buffer(*, info=None):  # pylint: disable=unused-argument
    """A model to complete on open tabs across all windows.

    Used for switching the buffer command.
    """
    model = completionmodel.CompletionModel(column_widths=(6, 40, 54))
    #  return _buffer()
    return model


def other_buffer(*, info):
    """A model to complete on open tabs across all windows except the current.

    Used for the tab-take command.
    """
    model = completionmodel.CompletionModel(column_widths=(6, 40, 54))
    #  return _buffer()
    return model
    #  return _buffer(skip_win_id=info.win_id)


def window(*, info):
    """A model to complete on all open windows."""
    model = completionmodel.CompletionModel(column_widths=(6, 30, 64))

    windows = []

    for win_id in objreg.window_registry:
        if win_id == info.win_id:
            continue
        tabbed_browser = objreg.get('tabbed-browser', scope='window',
                                    window=win_id)
        tab_titles = (tab.title() for tab in tabbed_browser.widgets())
        windows.append(("{}".format(win_id),
                        objreg.window_registry[win_id].windowTitle(),
                        ", ".join(tab_titles)))

    model.add_category(listcategory.ListCategory("Windows", windows))

    return model
