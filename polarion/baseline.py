from polarion.document import Document
from polarion.project import Project
from polarion.user import User


class Baseline(object):
    """
    A Polarion baseline instance

    :param polarion: Polarion client object
    :param polarion_record: The baseline record
    """

    def __init__(self, polarion, polarion_record=None, rev_uri=None):
        self._polarion = polarion
        self._polarion_record = polarion_record

        if rev_uri is not None:
            service = self._polarion.getService('Tracker')
            self._polarion_record = service.getRevisionByUri(self._revision)

        if self._polarion_record is not None and not self._polarion_record.unresolvable:
            self._revision = polarion_record.baseRevision

            polarion_attributes = self._polarion_record.__dict__["__values__"]

            # parse all polarion attributes to this class
            for attr, value in polarion_attributes.items():
                if attr == "author":
                    self.author = User(polarion, polarion_record=value)
                elif attr == "project":
                    self.project = Project(polarion, value['id'])
                else:
                    setattr(self, attr, value)
        else:
            raise Exception(f'Baseline not retrieved from Polarion')

    def queryModulesInBaseline(self, query='*:*', sort='*'):

        elements = [
            "attachments",
            "comments",
            "created",
            "id",
            "location",
            "project",
            "status",
            "title",
            "type",
            "updated"
        ]
        service = self._polarion.getService('Tracker')
        modules = service.queryModulesInBaseline(query, sort, self._revision, elements, -1)
        return [Document(self._polarion, self.project, module.uri) for module in modules]