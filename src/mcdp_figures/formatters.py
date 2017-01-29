from abc import abstractmethod, ABCMeta


class MakeFigures_Formatter():
    __metaclass__ = ABCMeta
    
    @abstractmethod
    def available_formats(self):
        """ Returns a set of formats that are available """
    
    @abstractmethod    
    def get(self, mf, formats):
        """
            mf: MakeFiguresNDP
            formats: tuple of strings
            
            must return a tuple of same length as formats
        """
        
class TextFormatter(MakeFigures_Formatter):
    def available_formats(self):
        return ['txt']
    
    def get(self, mf, formats):
        text = self.get_text(mf)
        
        if isinstance(formats, str):
            assert formats == 'txt'
            return text
        else:
            assert formats[0] == 'txt'
            return (text,)
        
    @abstractmethod
    def get_text(self, mf):
        pass

class GGFormatter(MakeFigures_Formatter):

    def available_formats(self):
        return ['png', 'pdf', 'svg', 'dot']
    
    def get(self, mf, formats):
        from mcdp_report.gg_utils import gg_get_formats
        
#         with timeit_wall('GGFormatter - get_gg'):
        gg = self.get_gg(mf)
            
        if isinstance(formats, str):
            res, = gg_get_formats(gg, (formats,))
        else:
            res = gg_get_formats(gg, formats)
        return res

    @abstractmethod
    def get_gg(self, mf):
        pass
