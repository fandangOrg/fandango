

def update_connection(self, id, body, **kwargs):
    """
    Updates a connection

    This method makes a synchronous HTTP request by default. To make an
    asynchronous HTTP request, please define a `callback` function
    to be invoked when receiving the response.
    >>> def callback_function(response):
    >>>     pprint(response)
    >>>
    >>> thread = api.update_connection(id, body, callback=callback_function)

    :param callback function: The callback function
        for asynchronous request. (optional)
    :param str id: The connection id. (required)
    :param ConnectionEntity body: The connection configuration details. (required)
    :return: ConnectionEntity
             If the method is called asynchronously,
             returns the request thread.
    """
    kwargs['_return_http_data_only'] = True
    if kwargs.get('callback'):
        return self.update_connection_with_http_info(id, body, **kwargs)
    else:
        (data) = self.update_connection_with_http_info(id, body, **kwargs)
        return data


def update_connection_with_http_info(self, id, body, **kwargs):
    """
    Updates a connection

    This method makes a synchronous HTTP request by default. To make an
    asynchronous HTTP request, please define a `callback` function
    to be invoked when receiving the response.
    >>> def callback_function(response):
    >>>     pprint(response)
    >>>
    >>> thread = api.update_connection_with_http_info(id, body, callback=callback_function)

    :param callback function: The callback function
        for asynchronous request. (optional)
    :param str id: The connection id. (required)
    :param ConnectionEntity body: The connection configuration details. (required)
    :return: ConnectionEntity
             If the method is called asynchronously,
             returns the request thread.
    """

    all_params = ['id', 'body']
    all_params.append('callback')
    all_params.append('_return_http_data_only')
    all_params.append('_preload_content')
    all_params.append('_request_timeout')

    params = locals()
    for key, val in iteritems(params['kwargs']):
        if key not in all_params:
            raise TypeError(
                "Got an unexpected keyword argument '%s'"
                " to method update_connection" % key
            )
        params[key] = val
    del params['kwargs']
    # verify the required parameter 'id' is set
    if ('id' not in params) or (params['id'] is None):
        raise ValueError("Missing the required parameter `id` when calling `update_connection`")
    # verify the required parameter 'body' is set
    if ('body' not in params) or (params['body'] is None):
        raise ValueError("Missing the required parameter `body` when calling `update_connection`")

    collection_formats = {}

    path_params = {}
    if 'id' in params:
        path_params['id'] = params['id']

    query_params = []

    header_params = {}

    form_params = []
    local_var_files = {}

    body_params = None
    if 'body' in params:
        body_params = params['body']
    # HTTP header `Accept`
    header_params['Accept'] = self.api_client. \
        select_header_accept(['application/json'])

    # HTTP header `Content-Type`
    header_params['Content-Type'] = self.api_client. \
        select_header_content_type(['application/json'])

    # Authentication setting
    auth_settings = ['tokenAuth']

    return self.api_client.call_api('/connections/{id}', 'PUT',
                                    path_params,
                                    query_params,
                                    header_params,
                                    body=body_params,
                                    post_params=form_params,
                                    files=local_var_files,
                                    response_type='ConnectionEntity',
                                    auth_settings=auth_settings,
                                    callback=params.get('callback'),
                                    _return_http_data_only=params.get('_return_http_data_only'),
                                    _preload_content=params.get('_preload_content', True),
                                    _request_timeout=params.get('_request_timeout'),
                                    collection_formats=collection_formats)


def create_processor(self, id, body, **kwargs):
    """
    Creates a new processor

    This method makes a synchronous HTTP request by default. To make an
    asynchronous HTTP request, please define a `callback` function
    to be invoked when receiving the response.
    >>> def callback_function(response):
    >>>     pprint(response)
    >>>
    >>> thread = api.create_processor(id, body, callback=callback_function)

    :param callback function: The callback function
        for asynchronous request. (optional)
    :param str id: The process group id. (required)
    :param ProcessorEntity body: The processor configuration details. (required)
    :return: ProcessorEntity
             If the method is called asynchronously,
             returns the request thread.
    """
    kwargs['_return_http_data_only'] = True
    if kwargs.get('callback'):
        return self.create_processor_with_http_info(id, body, **kwargs)
    else:
        (data) = self.create_processor_with_http_info(id, body, **kwargs)
        return data


def create_processor_with_http_info(self, id, body, **kwargs):
    """
    Creates a new processor

    This method makes a synchronous HTTP request by default. To make an
    asynchronous HTTP request, please define a `callback` function
    to be invoked when receiving the response.
    >>> def callback_function(response):
    >>>     pprint(response)
    >>>
    >>> thread = api.create_processor_with_http_info(id, body, callback=callback_function)

    :param callback function: The callback function
        for asynchronous request. (optional)
    :param str id: The process group id. (required)
    :param ProcessorEntity body: The processor configuration details. (required)
    :return: ProcessorEntity
             If the method is called asynchronously,
             returns the request thread.
    """

    all_params = ['id', 'body']
    all_params.append('callback')
    all_params.append('_return_http_data_only')
    all_params.append('_preload_content')
    all_params.append('_request_timeout')

    params = locals()
    for key, val in iteritems(params['kwargs']):
        if key not in all_params:
            raise TypeError(
                "Got an unexpected keyword argument '%s'"
                " to method create_processor" % key
            )
        params[key] = val
    del params['kwargs']
    # verify the required parameter 'id' is set
    if ('id' not in params) or (params['id'] is None):
        raise ValueError("Missing the required parameter `id` when calling `create_processor`")
    # verify the required parameter 'body' is set
    if ('body' not in params) or (params['body'] is None):
        raise ValueError("Missing the required parameter `body` when calling `create_processor`")

    collection_formats = {}

    path_params = {}
    if 'id' in params:
        path_params['id'] = params['id']

    query_params = []

    header_params = {}

    form_params = []
    local_var_files = {}

    body_params = None
    if 'body' in params:
        body_params = params['body']
    # HTTP header `Accept`
    header_params['Accept'] = self.api_client. \
        select_header_accept(['application/json'])

    # HTTP header `Content-Type`
    header_params['Content-Type'] = self.api_client. \
        select_header_content_type(['application/json'])

    # Authentication setting
    auth_settings = ['tokenAuth']

    return self.api_client.call_api('/process-groups/{id}/processors', 'POST',
                                    path_params,
                                    query_params,
                                    header_params,
                                    body=body_params,
                                    post_params=form_params,
                                    files=local_var_files,
                                    response_type='ProcessorEntity',
                                    auth_settings=auth_settings,
                                    callback=params.get('callback'),
                                    _return_http_data_only=params.get('_return_http_data_only'),
                                    _preload_content=params.get('_preload_content', True),
                                    _request_timeout=params.get('_request_timeout'),
                                    collection_formats=collection_formats)




def create_processor(parent_pg, processor, location, name=None, config=None):
    """
    Instantiates a given processor on the canvas

    Args:
        parent_pg (ProcessGroupEntity): The parent Process Group
        processor (DocumentedTypeDTO): The abstract processor type object to be
            instantiated
        location (tuple[x, y]): The location coordinates
        name (Optional [str]):  The name for the new Processor
        config (Optional [ProcessorConfigDTO]): A configuration object for the
            new processor

    Returns:
         (ProcessorEntity): The new Processor

    """
    if name is None:
        processor_name = processor.type.split('.')[-1]
    else:
        processor_name = name
    if config is None:
        target_config = nipyapi.nifi.ProcessorConfigDTO()
    else:
        target_config = config
    try:
        return nipyapi.nifi.ProcessGroupsApi().create_processor(
            id=parent_pg.id,
            body=nipyapi.nifi.ProcessorEntity(
                revision={'version': 0},
                component=nipyapi.nifi.ProcessorDTO(
                    position=nipyapi.nifi.PositionDTO(
                        x=float(location[0]),
                        y=float(location[1])
                    ),
                    type=processor.type,
                    name=processor_name,
                    config=target_config
                )
            )
        )
    except nipyapi.nifi.rest.ApiException as e:
        raise ValueError(e.body)




def create_connection(parent_pg, source, destination, name=None, config=None):
    """
    Instantiates a given processor on the canvas

    Args:
        parent_pg (ProcessGroupEntity): The parent Process Group
        processor (DocumentedTypeDTO): The abstract processor type object to be
            instantiated
        location (tuple[x, y]): The location coordinates
        name (Optional [str]):  The name for the new Processor
        config (Optional [ProcessorConfigDTO]): A configuration object for the
            new processor

    Returns:
         (ProcessorEntity): The new Processor

    """
    # if name is None:
    #     processor_name = processor.type.split('.')[-1]
    # else:
    #     processor_name = name
    if config is None:
        target_config = nipyapi.nifi.ProcessorConfigDTO()
    else:
        target_config = config
    try:
        return nipyapi.nifi.ProcessGroupsApi().create_processor(
            id=parent_pg.id,
            body=nipyapi.nifi.ConnectionEntity(
                revision={'version': 0},
                component=nipyapi.nifi.DTO(
                    position=nipyapi.nifi.PositionDTO(
                        x=float(location[0]),
                        y=float(location[1])
                    ),
                    type=processor.type,
                    name=processor_name,
                    config=target_config
                )
            )
        )
    except nipyapi.nifi.rest.ApiException as e:
        raise ValueError(e.body)

