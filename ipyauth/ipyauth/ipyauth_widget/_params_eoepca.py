
import json

from copy import deepcopy as copy
from traitlets import HasTraits, Unicode, validate, TraitError

from ._util import Util

class ParamsEoepca(HasTraits):

    name = Unicode()
    response_type = Unicode()
    response_mode = Unicode()
    authorize_endpoint = Unicode()
    client_id = Unicode()
    redirect_uri = Unicode()
    scope = Unicode()
    access_type = Unicode()
    prompt = Unicode()
    display = Unicode()
    nonce = Unicode()

    def __init__(self,
                 name='eoepca',
                 response_type=None,
                 client_id=None,
                 redirect_uri=None,
                 scope=None,
                 prompt=None,
                 display=None,
                 nonce=None,
                 response_mode=None,
                 dotenv_file=None,
                 dotenv_folder='/ipyauth/notebooks'
                 ):
        """
        """
        dic = Util.load_dotenv(dotenv_folder,
                               dotenv_file,
                               name)

        for k, v in dic.items():
            setattr(self, k, v)
            
        self.name = name

        # overrides
        if response_type:
            self.response_type = response_type
        if client_id:
            self.client_id = client_id
        if redirect_uri:
            self.redirect_uri = redirect_uri
        if scope:
            self.scope = scope
        if prompt:
            self.prompt = prompt
        if display:
            self.display = display
        if nonce:
            self.nonce = nonce
        if response_mode:
            self.response_mode = response_mode

        self.data = self.build_data()

    def to_dict(self):
        """
        """
        d = copy(self.__dict__)
        d = {k: v for k, v in d.items() if v is not None}
        return d

    def __repr__(self):
        """
        """
        return json.dumps(self.data, sort_keys=False, indent=2)

    @validate('response_type')
    def _valid_response_type(self, proposal):
        """
        """
        return proposal['value']

    @validate('redirect_uri')
    def _valid_redirect_uri(self, proposal):
        """
        """
        if not Util.is_url(proposal['value']):
            raise TraitError('redirect_uri must be an https url')
        return proposal['value']

    @validate('scope')
    def _valid_scope(self, proposal):
        """
        """
        elmts = proposal['value'].split(' ')
        if not ('profile' in elmts) and not ('openid' in elmts):
            raise TraitError('scope must contain "profile" and "openid"')
        return proposal['value']

    def build_data(self):
        """
        """
        props_params = ['name',
                        ]
        props_url_params = ['response_type',
                            'client_id',
                            'redirect_uri',
                            'scope',
                            'prompt',
                            'display',
                            'nonce',
                            'response_mode'
                            ]

        data = {}
        for k in props_params:
            v = getattr(self, k)
            if v != '':
                data[k] = v

        data_url = {}
        for k in props_url_params:
            v = getattr(self, k)
            if v != '':
                data_url[k] = v

        data['url_params'] = data_url

        return data
