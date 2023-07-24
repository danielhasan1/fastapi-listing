from typing import NamedTuple, Callable, Optional

from fastapi import Request

from fastapi_listing.abstracts import ListingServiceBase
from fastapi_listing.dao.generic_dao import GenericDao
from fastapi_listing.factory import strategy_factory
from fastapi_listing.dao import dao_factory
from fastapi_listing.service.adapters import CoreListingParamsAdapter
from fastapi_listing.interface.client_site_params_adapter import ClientSiteParamAdapter


class ListingService(ListingServiceBase):  # noqa
    filter_mapper: dict = {}
    sort_mapper: dict = {}
    # here resource creation should be based on factory and not inline as we are separating creation from usage.
    # factory should deliver sorting resource
    # default_srt_on: str = "created_at" # to be taken by user at child class level
    default_srt_ord: str = "dsc"
    paginate_strategy: str = "default_paginator"
    query_strategy: str = "default_query"
    sorting_strategy: str = "default_sorter"
    sort_mecha: str = "indi_sorter_interceptor"
    filter_mecha: str = "iterative_filter_interceptor"
    default_page_size: int = 10
    default_dao: GenericDao = GenericDao
    feature_params_adapter: ClientSiteParamAdapter = CoreListingParamsAdapter

    # pydantic_serializer: Type[BaseModel] = None
    # allowed_pydantic_custom_fields: bool = False
    # it is possible to have more than one serializer for particular endpoint depending upon
    # user or a query/path param condition we could switch json schema so allowing this
    # flexibility for the user to be able to switch between schema Fastapilisting object
    # should get initialized at user level and not implicit.

    def __init__(self, request: Request, **kwargs) -> None:
        self.request = request
        self.extra_context = kwargs
        self.dao: ListingService.default_dao = dao_factory.create(self.default_dao.name)

    def get_listing(self):
        """
        implement at child class level.

        FastapiListing(self.request, self.dao, pydantic_serializer=some_pydantic_model_class,
         custom_fields=True/False).get_response(self.MetaInfo(self))
        custom_fields can be also called pydantic_custom_fields.
        Note: what is pydantic_custom_fields?
                These are the fields that gets generated at runtime from existing table/sqlalchemy model fields.
                for example:
                lets say you have a pydantic model class
                class abc(BaseModel):
                    id: int
                    code: str

                    @root_validator
                    def generate_code(cls, values):
                        values["code"] = f'FANCY{values["id"]}CODE'
                here code gets generated at runtime, code is not a table field, code is a custom field that is
                deduced with the help of id.
        :return: page response for client to render
        """
        raise NotImplementedError("method should be implemented in child class and not here!")

    class MetaInfo:

        def __init__(self, outer_instance):
            self.paginating_strategy = strategy_factory.create(
                outer_instance.paginate_strategy, request=outer_instance.request)
            self.filter_column_mapper = outer_instance.filter_mapper
            self.query_strategy = strategy_factory.create(outer_instance.query_strategy)
            self.sorting_column_mapper = outer_instance.sort_mapper
            self.default_sort_val = dict(type=outer_instance.default_srt_ord,
                                         field=outer_instance.default_srt_on)
            self.sorting_strategy = strategy_factory.create(
                outer_instance.sorting_strategy,
                model=outer_instance.dao.model,
                request=outer_instance.request,
            )
            self.sorter_mechanic = outer_instance.sort_mecha
            self.filter_mechanic = outer_instance.filter_mecha
            self.extra_context = outer_instance.extra_context
            self.feature_params_adapter = outer_instance.feature_params_adapter(outer_instance.request)
            self.default_page_size = outer_instance.default_page_size

    # @staticmethod
    # def get_sort_mecha_plugin_path() -> str:
    #     """
    #     hook to provide sort mecha plugin module path as py import path
    #     overwrite allowed to provide custom path.
    #     :return: import path as string ex. fastapi_listing.interceptors.sorter_mechanics.
    #     """
    #     return "fastapi_listing.interceptors.sorter_mechanics"
    #
    # @staticmethod
    # def get_filter_mecha_plugin_path() -> str:
    #     """
    #    hook to provide filter mecha plugin module path as py import path
    #    overwrite allowed to provide custom path.
    #    :return: import path as string ex. fastapi_listing.interceptors.filter_mechanics.
    #    """
    #     return "fastapi_listing.interceptors.filter_mechanics"
    #
    # @classmethod
    # def plugins_to_load(cls) -> list[str]:
    #     """
    #     Provided a hook to be called at module level of each listing service.
    #     overwrite sort or filter plugin path getters to give your own custom
    #     mechanic implementations.
    #     refrain from overwriting it as this may change or it's fundamnetal
    #     implementation is already broken down to pieces that can no longer
    #     be broken any further. So instead of overwriting this
    #     overwrite the individual pieces
    #     :return: list plugins to load
    #     currently only support sort/filter mecha loading
    #     todo: can add pattern calling like %s_plugin_path for providing n number of plugin loading
    #     """
    #     return [cls.get_sort_mecha_plugin_path(), cls.get_filter_mecha_plugin_path()]

# calling loader at module level so once the module is loaded all plugins get loaded and not further loading is required
# loader.load_plugins(ListingService.plugins_to_load())


# todo: how to provide a hook in listing service so a person can easily overwrite the data list or manipulate it easily
# todo: before wrapping it up in page response


# page modifier has become abstract method in child class
#
# metainfo is causing issue due to its attributes types
#
# plugin is causing issue becuase when we load plugin in our child class first the module loads default plugin then our child class loads plugin
# if one plugin is already loaded from our core module then child module tries to load it again and it shows error


# appr 1 - we could centralise the loading process but it would benefit if we could understand plugin pattern in more depth
