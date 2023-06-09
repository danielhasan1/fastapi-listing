from fastapi import Request

from fastapi_listing.abstracts import ListingServiceBase
from fastapi_listing.dao.generic_dao import GenericDao
from fastapi_listing.factory import strategy_factory
from fastapi_listing.interface.listing_meta_info import ListingMetaInfo


class ListingService(ListingServiceBase):  # noqa
    filter_mapper: dict = {}
    sort_mapper: dict = {}
    # here resource creation should be based on factory and not inline as we are separating creation from usage.
    # factory should deliver sorting resource
    # DEFAULT_SRT_ON: str = "created_at" # to be taken by user at child class level
    DEFAULT_SRT_ORD: str = "dsc"
    PAGINATE_STRATEGY: str = "default_paginator"
    QUERY_STRATEGY: str = "default_query"
    SORTING_STRATEGY: str = "default_sorter"
    SORT_MECHA: str = "singleton_sorter_mechanics"
    FILTER_MECHA: str = "iterative_filter_mechanics"
    dao_kls: GenericDao = GenericDao

    # pydantic_serializer: Type[BaseModel] = None
    # allowed_pydantic_custom_fields: bool = False
    # it is possible to have more than one serializer for particular endpoint depending upon
    # user or a query/path param condition we could switch json schema so allowing this
    # flexibility for the user to be able to switch between schema Fastapilisting object
    # should get initialized at user level and not implicit.

    def __init__(self, request: Request, read_db=None, write_db=None, **kwargs) -> None:
        # self.dao = self.dao_kls(**kwargs)
        # pop out db sessions as they are concrete property of data access layer and not service layer.
        self.request = request
        self.extra_context = kwargs
        # ideally dao shouldn't have anything to do with extra_context i.e., kwargs
        # but in case someone could find any use of it we pushed prepare_dap below
        # so user could hack prepare_dao hook to do unwanted things.
        self._prepare_dao(read_db, write_db)

    def _prepare_dao(self, read_db, write_db):
        self.dao = self.dao_kls(read_db=read_db, write_db=write_db)
        # once dao is prepared and linked with listing service
        # we don't need it's dependent params anymore.
        # to only allowing db access on a single layer i.e. dao (data access object layer)
        # in case user has only one db for read/write
        # they can send read_db = write_db = db
        # both variable will still refer to same session

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

    # def page_data_modifier(self, data: dict) -> dict:
    #     raise NotImplementedError

    class MetaInfo:

        def __init__(self, outer_instance):
            self.paginating_strategy = strategy_factory.create(
                outer_instance.PAGINATE_STRATEGY)
            self.filter_column_mapper = outer_instance.filter_mapper
            self.query_strategy = strategy_factory.create(outer_instance.QUERY_STRATEGY)
            self.sorting_column_mapper = outer_instance.sort_mapper
            self.default_sort_val = dict(type=outer_instance.DEFAULT_SRT_ORD,
                                         field=outer_instance.DEFAULT_SRT_ON)
            self.sorting_strategy = strategy_factory.create(
                outer_instance.SORTING_STRATEGY,
                model=outer_instance.dao.model,
                request=outer_instance.request
            )
            self.sorter_mechanic = outer_instance.SORT_MECHA
            self.filter_mechanic = outer_instance.FILTER_MECHA
            self.extra_context = outer_instance.extra_context

    def meta_info_generator(self) -> ListingMetaInfo:
        return ListingService.MetaInfo(self)  # type:ignore # noqa # some issue is coming in pycharm for return types

    # @staticmethod
    # def get_sort_mecha_plugin_path() -> str:
    #     """
    #     hook to provide sort mecha plugin module path as py import path
    #     overwrite allowed to provide custom path.
    #     :return: import path as string ex. fastapi_listing.mechanics.sorter_mechanics.
    #     """
    #     return "fastapi_listing.mechanics.sorter_mechanics"
    #
    # @staticmethod
    # def get_filter_mecha_plugin_path() -> str:
    #     """
    #    hook to provide filter mecha plugin module path as py import path
    #    overwrite allowed to provide custom path.
    #    :return: import path as string ex. fastapi_listing.mechanics.filter_mechanics.
    #    """
    #     return "fastapi_listing.mechanics.filter_mechanics"
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
