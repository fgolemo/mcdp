class RepoView(object):
    
    def get_shelves(self):
        ''' Returns a dictionary of Bundles present in this repo. '''
        return self.shelves
    
    def get_desc_short(self):
        return self.info.desc_short
    
    def get_desc_long(self):
        return self.info.desc_long