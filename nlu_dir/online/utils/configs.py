from online.utils.nameutil import FieldClassifyNames as dcname,ContextNames as cname
from common.pathutil import PathUtil
_pathutil_class=PathUtil()


domain2entity2paths_set={dcname.product.value:
                                  {cname.domain.value:[_pathutil_class.domain_filepath,
                                                       ],
                                   cname.property.value:[_pathutil_class.property_filepath,
                                                        ]
                                    },
                              dcname.company.value:
                                  {cname.domain.value: [_pathutil_class.company_domain_filepath,
                                                        _pathutil_class.fufilled_company_domain_filepath
                                                        ],
                                   cname.property.value: [_pathutil_class.company_property_filepath
                                                          ]
                                   }
                              }

_environ='local'
# _environ='online'