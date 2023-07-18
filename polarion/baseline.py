import re
from polarion.document import Document
from polarion.project import Project
from polarion.user import User

import re

def extract_module_and_document(input_string):
    pattern = r'subterra:data-service:objects:/default/(\w+)\$\{Module\}\{moduleFolder\}(.*)#(.*)%.*'
    match = re.search(pattern, input_string)
    if match:
        return match.group(1), match.group(2), match.group(3)
    else:
        return None, None, None

class Baseline(object):
    """
    A Polarion baseline instance

    :param polarion: Polarion client object
    :param polarion_record: The baseline record
    """

    def __init__(self, polarion, polarion_record=None, rev_uri=None, owningproject=None):
        self._polarion = polarion
        self._polarion_record = polarion_record
        self._owningproject = owningproject
        self.singledocument = None
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
            # parse in case this is a single document revision
            if hasattr(self, 'baseObjectURI'):
                if '${project}' not in self.baseObjectURI:
                    # Single document revision
                    self.singledocument = self.baseObjectURI
        else:
            raise Exception(f'Baseline not retrieved from Polarion')
                
    def _formatquery(self, query):
        if not self._owningproject:
            return query
        
        if query == '*:*':
            return f'project.id:{self._owningproject}'
        
        return f'{query} AND project.id:{self._owningproject}'
    
    def queryModulesInBaseline(self, query='*:*', sort='*'):
        """
        Put query as 'project.id:<projectID>' to get documents in a specific project.
        """
        projectid = location = name = None
        if self.singledocument:
            projectid, location, name = extract_module_and_document(self.singledocument)

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
        if name != None:
            return [Document(self._polarion, self.project, module.uri) for module in modules if module.id == name]
        return [Document(self._polarion, self.project, module.uri) for module in modules]

    def __repr__(self) -> str:
        return f'Baseline at revno {self._revision}'