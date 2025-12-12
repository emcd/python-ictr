# vim: set filetype=python fileencoding=utf-8:
# -*- coding: utf-8 -*-

#============================================================================#
#                                                                            #
#  Licensed under the Apache License, Version 2.0 (the "License");           #
#  you may not use this file except in compliance with the License.          #
#  You may obtain a copy of the License at                                   #
#                                                                            #
#      http://www.apache.org/licenses/LICENSE-2.0                            #
#                                                                            #
#  Unless required by applicable law or agreed to in writing, software       #
#  distributed under the License is distributed on an "AS IS" BASIS,         #
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  #
#  See the License for the specific language governing permissions and       #
#  limitations under the License.                                            #
#                                                                            #
#============================================================================#


''' Dispatchers for messages and inspections to scribes. '''


from . import __
from . import configuration as _cfg
from . import exceptions as _exceptions
from . import flavors as _flavors
from . import printers as _printers
from . import reporters as _reporters
from . import textualizers as _texts


_installer_mutex: __.threads.Lock = __.threads.Lock( )
_registrar_mutex: __.threads.Lock = __.threads.Lock( )
_self_addresscfg: _cfg.AddressConfiguration = _cfg.AddressConfiguration(
    flavors = __.immut.Dictionary(
        note = _cfg.FlavorConfiguration(
            compositor_factory = (
                _texts.produce_compositor_factory_default(
                    introducer = 'NOTE| ' ) ) ),
        error = _cfg.FlavorConfiguration(
            compositor_factory = (
                _texts.produce_compositor_factory_default(
                    introducer = 'ERROR| ' ) ) ) ) )
_validate_arguments = (
    __.validate_arguments(
        globalvars = globals( ),
        errorclass = _exceptions.ArgumentClassInvalidity ) )


class AddressesConfigurationsRegistry(
    __.accret.Dictionary[ str, _cfg.AddressConfiguration ]
):
    # TODO: Use 'accret.ValidatorDictionary'.
    ''' Accretive dictionary specifically for address registrations. '''

    def __init__(
        self,
        *iterables: __.DictionaryPositionalArgument[
            str, _cfg.AddressConfiguration ],
        **entries: __.DictionaryNominativeArgument[
            _cfg.AddressConfiguration ],
    ):
        super( ).__init__( { __.package_name: _self_addresscfg } )
        self.update( *iterables, **entries )


class Omniflavor( __.enum.Enum ):
    ''' Singleton to match any flavor. '''

    Instance = __.enum.auto( )


ActiveFlavors: __.typx.TypeAlias = Omniflavor | frozenset[ _flavors.Flavor ]
ActiveFlavorsLiberal: __.typx.TypeAlias = __.typx.Union[
    Omniflavor,
    __.cabc.Sequence[ _flavors.Flavor ],
    __.cabc.Set[ _flavors.Flavor ],
]
ActiveFlavorsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ __.typx.Optional[ str ], ActiveFlavors ] )
ActiveFlavorsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ __.typx.Optional[ str ], ActiveFlavorsLiberal ] )
AddressesConfigurationsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ str, _cfg.AddressConfiguration ] )
ReportersRegistry: __.typx.TypeAlias = (
    __.accret.Dictionary[
        tuple[ str, _flavors.Flavor ], _reporters.Reporter ] )
TraceLevelsRegistry: __.typx.TypeAlias = (
    __.immut.Dictionary[ __.typx.Optional[ str ], int ] )
TraceLevelsRegistryLiberal: __.typx.TypeAlias = (
    __.cabc.Mapping[ __.typx.Optional[ str ], int ] )


def _provide_active_flavors_default( ) -> ActiveFlavorsRegistry:
    ''' Provides default set of globally active flavors. '''
    flavors = set( _flavors.flavor_specifications_standard.keys( ) )
    flavors.update( _flavors.flavor_aliases_standard.keys( ) )
    return __.immut.Dictionary( { None: frozenset( flavors ) } )


builtins_alias_default: __.typx.Annotated[
    str,
    __.typx.Doc(
        ''' Default alias for global dispatcher in builtins module. ''' ),
] = 'ictr'
addresscfgs: __.typx.Annotated[
    AddressesConfigurationsRegistry,
    __.typx.Doc( ''' Global registry of address configurations. ''' ),
] = AddressesConfigurationsRegistry( )
omniflavor: __.typx.Annotated[
    Omniflavor, __.typx.Doc( ''' Matches any flavor. ''' )
] = Omniflavor.Instance


class Dispatcher( __.immut.DataclassObject ):
    ''' Provides reporter instances. '''

    active_flavors: __.typx.Annotated[
        ActiveFlavorsRegistry,
        __.typx.Doc(
            ''' Mapping of addresses to active flavor sets.

                Key ``None`` applies globally. Address-specific entries
                override globals for that address.
            ''' ),
    ] = __.dcls.field( default_factory = _provide_active_flavors_default )
    addresscfgs: __.typx.Annotated[
        AddressesConfigurationsRegistry,
        __.typx.Doc(
            ''' Registry of per-address configurations.

                Addresses inherit configuration from their parent packages.
                Top-level packages inherit from general instance
                configruration.
            ''' ),
    ] = __.dcls.field( default_factory = lambda: addresscfgs )
    generalcfg: __.typx.Annotated[
        _cfg.DispatcherConfiguration,
        __.typx.Doc(
            ''' General configuration.

                Top of configuration inheritance hierarchy.
                Default is suitable for application use.
            ''' ),
    ] = __.dcls.field( default_factory = _cfg.DispatcherConfiguration )
    printer_factories: __.typx.Annotated[
        _printers.PrinterFactoriesUnion,
        __.typx.Doc(
            ''' Factories which produce callables to output text somewhere.

                A factory takes two arguments, address and flavor, and
                returns a callable which takes one argument, either a record
                or the string produced by a textualizer.

                May also be writable text stream instead of a factory.
            ''' ),
    ] = ( _printers.produce_printer_factory_default( __.sys.stderr ), )
    reporters: __.typx.Annotated[
        ReportersRegistry,
        __.typx.Doc(
            ''' Cache of reporter instances by address and flavor. ''' ),
    ] = __.dcls.field( default_factory = ReportersRegistry )
    # TODO? Move reporters mutex into reporters registry.
    reporters_mutex: __.typx.Annotated[
        __.threads.Lock,
        __.typx.Doc( ''' Access lock for cache of reporter instances. ''' ),
    ] = __.dcls.field( default_factory = __.threads.Lock )
    trace_levels: __.typx.Annotated[
        TraceLevelsRegistry,
        __.typx.Doc(
            ''' Mapping of addresses to maximum trace depths.

                Key ``None`` applies globally. Address-specific entries
                override globals for that address.
            ''' ),
    ] = __.dcls.field(
        default_factory = lambda: __.immut.Dictionary( { None: -1 } ) )

    @_validate_arguments
    def __call__(
        self,
        flavor: _flavors.Flavor, *,
        address: __.Absential[ str ] = __.absent,
    ) -> _reporters.Reporter:
        ''' Produces and caches message reporter. '''
        address = (
            _discover_invoker_module_name( ) if __.is_absent( address )
            else address )
        cache_index = ( address, flavor )
        if cache_index in self.reporters:
            with self.reporters_mutex:
                return self.reporters[ cache_index ]
        configuration = _produce_ic_configuration( self, address, flavor )
        if isinstance( flavor, int ):
            trace_level = (
                _calculate_effective_trace_level( self.trace_levels, address) )
            active = flavor <= trace_level
        elif isinstance( flavor, str ): # pragma: no branch
            active_flavors = (
                _calculate_effective_flavors( self.active_flavors, address ) )
            active = (
                isinstance( active_flavors, Omniflavor )
                or flavor in active_flavors )
        compositor = configuration[ 'compositor_factory' ]( address, flavor )
        printers = _resolve_printers( self.printer_factories, address, flavor )
        reporter = _reporters.Reporter(
            active = active, address = address, flavor = flavor,
            compositor = compositor, printers = printers )
        with self.reporters_mutex:
            self.reporters[ cache_index ] = reporter
        return reporter

    @_validate_arguments
    def install( self, alias: str = builtins_alias_default ) -> __.typx.Self:
        ''' Installs dispatcher into builtins with provided alias.

            Replaces an existing dispatcher. Preserves global address
            configurations.

            Library developers should call :py:func:`register_address` instead.
        '''
        import builtins
        with _installer_mutex:
            dispatcher_o = getattr( builtins, alias, None )
            if isinstance( dispatcher_o, Dispatcher ):
                self( 'note', address = __name__ )(
                    "Installed dispatcher is being replaced." )
                setattr( builtins, alias, self )
            else:
                __.install_builtin_safely(
                    alias, self, _exceptions.AttributeNondisplacement )
        return self

    @_validate_arguments
    def register_address(
        self,
        name: __.Absential[ str ] = __.absent,
        configuration: __.Absential[ _cfg.AddressConfiguration ] = __.absent,
    ) -> __.typx.Self:
        ''' Registers configuration for address.

            If no address is given, then the invoking module name is
            inferred.

            If no configuration is provided, then a default is generated.
        '''
        if __.is_absent( name ):
            name = _discover_invoker_module_name( )
        if __.is_absent( configuration ):
            configuration = _cfg.AddressConfiguration( )
        with _registrar_mutex:
            self.addresscfgs[ name ] = configuration
        return self


ActiveFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ ActiveFlavorsLiberal | ActiveFlavorsRegistryLiberal ],
    __.typx.Doc(
        ''' Flavors to activate.

            Can be collection, which applies globally across all registered
            addresses. Or, can be mapping of addresses to sets.

            Address-specific entries merge with global entries.
        ''' ),
]
AddressArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ str ],
    __.typx.Doc(
        ''' Address to register.

            If absent, infers the invoking module name as the address.
        ''' ),
]
AddresscfgsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ AddressesConfigurationsRegistryLiberal ],
    __.typx.Doc(
        ''' Address configurations for the dispatcher.

            If absent, defaults to global addresses registry.
        ''' ),
]
CompositorFactoryArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _texts.CompositorFactory ],
    __.typx.Doc(
        ''' Factory which produces compositor callable.

            Takes address and flavor as arguments.
            Returns compositor to convert record content to a string.
        ''' ),
]
EvnActiveFlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.typx.Optional[ str ] ],
    __.typx.Doc(
        ''' Name of environment variable for active flavors or ``None``.

            If absent, then a default environment variable name is used.

            If ``None``, then active flavors are not parsed from the process
            environment.

            If active flavors are supplied directly to a function,
            which also accepts this argument, then active flavors are not
            parsed from the process environment.
        ''' ),
]
EvnTraceLevelsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ __.typx.Optional[ str ] ],
    __.typx.Doc(
        ''' Name of environment variable for trace levels or ``None``.

            If absent, then a default environment variable name is used.

            If ``None``, then trace levels are not parsed from the process
            environment.

            If trace levels are supplied directly to a function,
            which also accepts this argument, then trace levels are not
            parsed from the process environment.
        ''' ),
]
FlavorsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.FlavorsRegistryLiberal ],
    __.typx.Doc( ''' Registry of flavor identifiers to configurations. ''' ),
]
GeneralcfgArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _cfg.DispatcherConfiguration ],
    __.typx.Doc(
        ''' General configuration for the dispatcher.

            Top of configuration inheritance hierarchy. If absent,
            defaults to a suitable configuration for application use.
        ''' ),
]
InstallAliasArgument: __.typx.TypeAlias = __.typx.Annotated[
    str,
    __.typx.Doc(
        ''' Alias under which the dispatcher is installed in builtins. ''' ),
]
IntroducerArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _texts.IntroducerUnion ],
    __.typx.Doc(
        ''' String or factory which produces message introduction.

            Factory takes textualization control, address, and flavor as
            arguments. Returns introduction string.
        ''' ),
]
PrinterFactoriesArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ _printers.PrinterFactoriesUnion ],
    __.typx.Doc(
        ''' Factories which produce callables to output text somewhere.

            A factory take two arguments, address and flavor, and
            returns a callable which takes one argument, either a record or
            the string produced by a textualizer.

            May also be writable text stream instead of a factory.

            If absent, uses a default.
        ''' ),
]
TraceLevelsArgument: __.typx.TypeAlias = __.typx.Annotated[
    __.Absential[ int | TraceLevelsRegistryLiberal ],
    __.typx.Doc(
        ''' Maximum trace depths.

            Can be an integer, which applies globally across all registered
            addresses. Or, can be a mapping of addresses to integers.

            Address-specific entries override global entries.
        ''' ),
]


def active_flavors_from_environment(
    evname: __.Absential[ str ] = __.absent
) -> ActiveFlavorsRegistry:
    ''' Extracts active flavors from named environment variable. '''
    active_flavors: ActiveFlavorsRegistryLiberal = { }
    name = 'ICTR_ACTIVE_FLAVORS' if __.is_absent( evname ) else evname
    value = __.os.getenv( name )
    if value is None:
        return _provide_active_flavors_default( )
    for part in value.split( '+' ):
        if not part: continue
        if ':' in part:
            address, flavors = part.split( ':', 1 )
        else: address, flavors = None, part
        match flavors:
            case '*': active_flavors[ address ] = omniflavor
            case _: active_flavors[ address ] = flavors.split( ',' )
    return __.immut.Dictionary( {
        address:
            flavors if isinstance( flavors, Omniflavor )
            else frozenset( flavors )
        for address, flavors in active_flavors.items( ) } )


def trace_levels_from_environment(
    evname: __.Absential[ str ] = __.absent
) -> TraceLevelsRegistry:
    ''' Extracts trace levels from named environment variable. '''
    trace_levels: TraceLevelsRegistryLiberal = { None: -1 }
    name = 'ICTR_TRACE_LEVELS' if __.is_absent( evname ) else evname
    value = __.os.getenv( name, '' )
    for part in value.split( '+' ):
        if not part: continue
        if ':' in part: address, level = part.split( ':', 1 )
        else: address, level = None, part
        if not level.isdigit( ):
            __.warnings.warn(
                f"Non-integer trace level {level!r} "
                f"in environment variable {name!r}." )
            continue
        trace_levels[ address ] = int( level )
    return __.immut.Dictionary( trace_levels )


@_validate_arguments
def install( # noqa: PLR0913
    alias: InstallAliasArgument = builtins_alias_default,
    active_flavors: ActiveFlavorsArgument = __.absent,
    generalcfg: GeneralcfgArgument = __.absent,
    printer_factories: PrinterFactoriesArgument = __.absent,
    trace_levels: TraceLevelsArgument = __.absent,
    evname_active_flavors: EvnActiveFlavorsArgument = __.absent,
    evname_trace_levels: EvnTraceLevelsArgument = __.absent,
) -> Dispatcher:
    ''' Produces dispatcher and installs it into builtins with alias.

        Replaces an existing dispatcher, preserving global address
        configurations.

        Library developers should call :py:func:`register_address` instead.
    '''
    dispatcher = produce_dispatcher(
        active_flavors = active_flavors,
        generalcfg = generalcfg,
        printer_factories = printer_factories,
        trace_levels = trace_levels,
        evname_active_flavors = evname_active_flavors,
        evname_trace_levels = evname_trace_levels )
    return dispatcher.install( alias = alias )


@_validate_arguments
def produce_dispatcher( # noqa: PLR0913
    active_flavors: ActiveFlavorsArgument = __.absent,
    generalcfg: GeneralcfgArgument = __.absent,
    addresscfgs: AddresscfgsArgument = __.absent,
    printer_factories: PrinterFactoriesArgument = __.absent,
    trace_levels: TraceLevelsArgument = __.absent,
    evname_active_flavors: EvnActiveFlavorsArgument = __.absent,
    evname_trace_levels: EvnTraceLevelsArgument = __.absent,
) -> Dispatcher:
    ''' Produces dispatcher with some shorthand argument values. '''
    # TODO: Deeper validation of active flavors and trace levels.
    # TODO: Deeper validation of printer factory.
    initargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( generalcfg ):
        initargs[ 'generalcfg' ] = generalcfg
    if not __.is_absent( addresscfgs ):
        initargs[ 'addresscfgs' ] = AddressesConfigurationsRegistry(
            {   address: configuration for address, configuration
                in addresscfgs.items( ) } )
    if not __.is_absent( printer_factories ):
        initargs[ 'printer_factories' ] = printer_factories
    _add_dispatcher_initarg_active_flavors(
        initargs, active_flavors, evname_active_flavors )
    _add_dispatcher_initarg_trace_levels(
        initargs, trace_levels, evname_trace_levels )
    return Dispatcher( **initargs )


@_validate_arguments
def register_address(
    name: AddressArgument = __.absent,
    flavors: FlavorsArgument = __.absent,
    compositor_factory: CompositorFactoryArgument = __.absent,
    introducer: IntroducerArgument = __.absent,
) -> _cfg.AddressConfiguration:
    ''' Registers address configuration on the builtin dispatcher.

        If no dispatcher exists in builtins, installs one which produces null
        printers.

        Intended for library developers to configure debugging flavors
        without overriding anything set by the application or other libraries.
        Application developers should call :py:func:`install` instead.
    '''
    import builtins
    dispatcher = getattr( builtins, builtins_alias_default, None )
    if not isinstance( dispatcher, Dispatcher ):
        dispatcher = Dispatcher( )
        __.install_builtin_safely(
            builtins_alias_default,
            dispatcher,
            _exceptions.AttributeNondisplacement )
    nomargs: dict[ str, __.typx.Any ] = { }
    if not __.is_absent( flavors ):
        nomargs[ 'flavors' ] = __.immut.Dictionary( flavors )
    if not __.is_absent( compositor_factory ):
        nomargs[ 'compositor_factory' ] = compositor_factory
    if not __.is_absent( introducer ):
        nomargs[ 'introducer' ] = introducer
    configuration = _cfg.AddressConfiguration( **nomargs )
    dispatcher.register_address( name = name, configuration = configuration )
    return configuration


def _add_dispatcher_initarg_active_flavors(
    initargs: dict[ str, __.typx.Any ],
    active_flavors: ActiveFlavorsArgument = __.absent,
    evname_active_flavors: EvnActiveFlavorsArgument = __.absent,
) -> None:
    name = 'active_flavors'
    if not __.is_absent( active_flavors ):
        if isinstance( active_flavors, Omniflavor ):
            initargs[ name ] = __.immut.Dictionary(
                { None: active_flavors } )
        elif isinstance( active_flavors, ( __.cabc.Sequence,  __.cabc.Set ) ):
            initargs[ name ] = __.immut.Dictionary(
                { None: frozenset( active_flavors ) } )
        else:
            initargs[ name ] = __.immut.Dictionary( {
                address:
                    flavors if isinstance( flavors, Omniflavor )
                    else frozenset( flavors )
                for address, flavors in active_flavors.items( ) } )
    elif evname_active_flavors is not None:
        initargs[ name ] = (
            active_flavors_from_environment( evname = evname_active_flavors ) )


def _add_dispatcher_initarg_trace_levels(
    initargs: dict[ str, __.typx.Any ],
    trace_levels: TraceLevelsArgument = __.absent,
    evname_trace_levels: EvnTraceLevelsArgument = __.absent,
) -> None:
    name = 'trace_levels'
    if not __.is_absent( trace_levels ):
        if isinstance( trace_levels, int ):
            initargs[ name ] = __.immut.Dictionary( { None: trace_levels } )
        else:
            trace_levels_: TraceLevelsRegistryLiberal = { None: -1 }
            trace_levels_.update( trace_levels )
            initargs[ name ] = __.immut.Dictionary( trace_levels_ )
    elif evname_trace_levels is not None:
        initargs[ name ] = (
            trace_levels_from_environment( evname = evname_trace_levels ) )


def _calculate_effective_flavors(
    flavors: ActiveFlavorsRegistry, address: str
) -> ActiveFlavors:
    result_ = flavors.get( None ) or frozenset( )
    if isinstance( result_, Omniflavor ): return result_
    result = result_
    for address_ in _iterate_address_ancestry( address ):
        if address_ in flavors:
            result_ = flavors.get( address_ ) or frozenset( )
            if isinstance( result_, Omniflavor ): return result_
            result |= result_
    return result


def _calculate_effective_trace_level(
    levels: TraceLevelsRegistry, address: str
) -> int:
    result = levels.get( None, -1 )
    for address_ in _iterate_address_ancestry( address ):
        if address_ in levels:
            result = levels[ address_ ]
    return result


def _dict_from_dataclass( objct: object ) -> dict[ str, __.typx.Any ]:
    # objct = __.typx.cast( _typeshed.DataclassInstance, objct )
    return {
        field.name: getattr( objct, field.name )
        for field in __.dcls.fields( objct ) # pyright: ignore[reportArgumentType]
        if not field.name.startswith( '_' ) }


def _discover_invoker_module_name( ) -> str:
    frame = __.inspect.currentframe( )
    while frame: # pragma: no branch
        module = __.inspect.getmodule( frame )
        if module is None:
            if '<stdin>' == frame.f_code.co_filename: # pragma: no cover
                name = '__main__'
                break
            raise _exceptions.ModuleInferenceFailure
        name = module.__name__
        if not name.startswith( f"{__.package_name}." ): break
        frame = frame.f_back
    return name


def _iterate_address_ancestry( name: str ) -> __.cabc.Iterator[ str ]:
    parts = name.split( '.' )
    for i in range( len( parts ) ):
        yield '.'.join( parts[ : i + 1 ] )


def _merge_ic_configuration(
    base: dict[ str, __.typx.Any ], update_objct: object,
) -> dict[ str, __.typx.Any ]:
    update: dict[ str, __.typx.Any ] = _dict_from_dataclass( update_objct )
    result: dict[ str, __.typx.Any ] = { }
    result[ 'flavors' ] = (
            dict( base.get( 'flavors', dict( ) ) )
        |   dict( update.get( 'flavors', dict( ) ) ) )
    for ename in ( 'compositor_factory', 'introducer' ):
        uvalue = update.get( ename )
        if uvalue is not None: result[ ename ] = uvalue
        elif ename in base: result[ ename ] = base[ ename ]
    return result


def _produce_ic_configuration(
    dispatcher: Dispatcher, address: str, flavor: _flavors.Flavor
) -> __.immut.Dictionary[ str, __.typx.Any ]:
    fconfigs: list[ _cfg.FlavorConfiguration ] = [ ]
    dconfig = dispatcher.generalcfg
    configd: dict[ str, __.typx.Any ] = {
        field.name: getattr( dconfig, field.name )
        for field in __.dcls.fields( dconfig )
        if not field.name.startswith( '_' ) }
    if flavor in dconfig.flavors:
        fconfigs.append( dconfig.flavors[ flavor ] )
    for address_ in _iterate_address_ancestry( address ):
        if address_ not in dispatcher.addresscfgs: continue
        mconfig = dispatcher.addresscfgs[ address_ ]
        configd = _merge_ic_configuration( configd, mconfig )
        if flavor in mconfig.flavors:
            fconfigs.append( mconfig.flavors[ flavor ] )
    if not fconfigs: raise _exceptions.FlavorInavailability( flavor )
    # Apply collected flavor configs after general and address configs.
    # (Applied in top-down order for correct overrides.)
    for fconfig in fconfigs:
        configd = _merge_ic_configuration( configd, fconfig )
    return __.immut.Dictionary( configd )


def _resolve_printer(
    factory: _printers.PrinterFactoryUnion,
    address: str,
    flavor: _flavors.Flavor,
) -> _printers.Printer:
    from .standard import Printer
    if isinstance( factory, __.io.TextIOBase ):
        return Printer( target = factory )
    return factory( address, flavor )


def _resolve_printers(
    factories: _printers.PrinterFactoriesUnion,
    address: str,
    flavor: _flavors.Flavor,
) -> _printers.Printers:
    return tuple(
        _resolve_printer( factory, address, flavor )
        for factory in factories )
