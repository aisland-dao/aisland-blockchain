use aisland_runtime::{
    get_all_module_accounts, opaque::SessionKeys, AccountId, AuthorityDiscoveryConfig,
    AuthorityDiscoveryId, BabeConfig, BalancesConfig, ContractsConfig, CurrencyId, EvmConfig,
    GenesisConfig, GrandpaConfig, ImOnlineId, IndicesConfig, MaxNativeTokenExistentialDeposit,
    SessionConfig, StakerStatus, StakingConfig, SudoConfig, SystemConfig, TokenSymbol,
    TokensConfig, AISC, WASM_BINARY,
};
use sc_service::{ChainType, Properties};
use sc_telemetry::TelemetryEndpoints;
use sp_consensus_babe::AuthorityId as BabeId;
use sp_core::{sr25519, Bytes, Pair, Public, H160};
use sp_finality_grandpa::AuthorityId as GrandpaId;
use sp_runtime::traits::IdentifyAccount;

use sc_chain_spec::ChainSpecExtension;
use sp_std::{collections::btree_map::BTreeMap, str::FromStr};

use serde::{Deserialize, Serialize};

use hex_literal::hex;
use sp_core::{bytes::from_hex, crypto::UncheckedInto};

use aisland_primitives::{AccountPublic, Balance, Nonce};

// The URL for the telemetry server.
const TELEMETRY_URL: &str = "wss://telemetry.polkadot.io/submit/";

/// Node `ChainSpec` extensions.
///
/// Additional parameters for some Substrate core modules,
/// customizable from the chain spec.
#[derive(Default, Clone, Serialize, Deserialize, ChainSpecExtension)]
#[serde(rename_all = "camelCase")]
pub struct Extensions {
    /// Block numbers with known hashes.
    pub fork_blocks: sc_client_api::ForkBlocks<aisland_primitives::Block>,
    /// Known bad block hashes.
    pub bad_blocks: sc_client_api::BadBlocks<aisland_primitives::Block>,
}

/// Specialized `ChainSpec`. This is a specialization of the general Substrate ChainSpec type.
pub type ChainSpec = sc_service::GenericChainSpec<GenesisConfig, Extensions>;

fn get_session_keys(
    grandpa: GrandpaId,
    babe: BabeId,
    im_online: ImOnlineId,
    authority_discovery: AuthorityDiscoveryId,
) -> SessionKeys {
    SessionKeys {
        babe,
        grandpa,
        im_online,
        authority_discovery,
    }
}

/// Helper function to generate a crypto pair from seed
pub fn get_from_seed<TPublic: Public>(seed: &str) -> <TPublic::Pair as Pair>::Public {
    TPublic::Pair::from_string(&format!("//{}", seed), None)
        .expect("static values are valid; qed")
        .public()
}

/// Helper function to generate an account ID from seed
pub fn get_account_id_from_seed<TPublic: Public>(seed: &str) -> AccountId
where
    AccountPublic: From<<TPublic::Pair as Pair>::Public>,
{
    AccountPublic::from(get_from_seed::<TPublic>(seed)).into_account()
}

/// Generate an authority keys.
pub fn get_authority_keys_from_seed(
    seed: &str,
) -> (
    AccountId,
    AccountId,
    GrandpaId,
    BabeId,
    ImOnlineId,
    AuthorityDiscoveryId,
) {
    (
        get_account_id_from_seed::<sr25519::Public>(&format!("{}//stash", seed)),
        get_account_id_from_seed::<sr25519::Public>(seed),
        get_from_seed::<GrandpaId>(seed),
        get_from_seed::<BabeId>(seed),
        get_from_seed::<ImOnlineId>(seed),
        get_from_seed::<AuthorityDiscoveryId>(seed),
    )
}

pub fn development_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "WASM binary not available".to_string())?;
    Ok(ChainSpec::from_genesis(
        // Name
        "Development",
        // ID
        "dev",
        ChainType::Development,
        move || {
            testnet_genesis(
                wasm_binary,
                // Initial PoA authorities
                vec![get_authority_keys_from_seed("Alice")],
                // Sudo account
                get_account_id_from_seed::<sr25519::Public>("Alice"),
                // Pre-funded accounts
                vec![
                    get_account_id_from_seed::<sr25519::Public>("Alice"),
                    get_account_id_from_seed::<sr25519::Public>("Bob"),
                    get_account_id_from_seed::<sr25519::Public>("Alice//stash"),
                    get_account_id_from_seed::<sr25519::Public>("Bob//stash"),
                ],
            )
        },
        // Bootnodes
        vec![],
        // Telemetry
        None,
        // Protocol ID
        None,
        // Properties
        Some(aisland_properties()),
        // Extensions
        Default::default(),
    ))
}

pub fn local_testnet_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "WASM binary not available".to_string())?;
    Ok(ChainSpec::from_genesis(
        // Name
        "Local Testnet",
        // ID
        "local_testnet",
        ChainType::Local,
        move || {
            testnet_genesis(
                wasm_binary,
                // Initial PoA authorities
                vec![
                    get_authority_keys_from_seed("Alice"),
                    get_authority_keys_from_seed("Bob"),
                ],
                // Sudo account
                get_account_id_from_seed::<sr25519::Public>("Alice"),
                // Pre-funded accounts
                vec![
                    get_account_id_from_seed::<sr25519::Public>("Alice"),
                    get_account_id_from_seed::<sr25519::Public>("Bob"),
                    get_account_id_from_seed::<sr25519::Public>("Charlie"),
                    get_account_id_from_seed::<sr25519::Public>("Dave"),
                    get_account_id_from_seed::<sr25519::Public>("Eve"),
                    get_account_id_from_seed::<sr25519::Public>("Ferdie"),
                    get_account_id_from_seed::<sr25519::Public>("Alice//stash"),
                    get_account_id_from_seed::<sr25519::Public>("Bob//stash"),
                    get_account_id_from_seed::<sr25519::Public>("Charlie//stash"),
                    get_account_id_from_seed::<sr25519::Public>("Dave//stash"),
                    get_account_id_from_seed::<sr25519::Public>("Eve//stash"),
                    get_account_id_from_seed::<sr25519::Public>("Ferdie//stash"),
                ],
            )
        },
        // Bootnodes
        vec![],
        // Telemetry
        // TelemetryEndpoints::new(vec![(TELEMETRY_URL.into(), 0)]).ok(),
        None,
        // Protocol ID
        Some("aisland_local_testnet"),
        // Properties
        Some(aisland_properties()),
        // Extensions
        Default::default(),
    ))
}

pub fn public_testnet_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "WASM binary not available".to_string())?;
    Ok(ChainSpec::from_genesis(
        // Name
        "Aisland Testnet",
        // ID
        "aisland_testnet",
        ChainType::Live,
        move || {
            testnet_genesis(
                wasm_binary,
                // Initial authorities keys:
                // stash
                // controller
                // grandpa
                // babe
                // im-online
                // authority-discovery
                vec![
                    (
                        // Boot Node/Validator 1: ip address 65.108.62.72 (public keys in hex)
                        hex!["28a1072ad74a525b78d207aeeb6faf16518e02936e8e9c47b74eb50485cc6e0b"]
                            .into(),
                        hex!["dab8b1ec5c466daad27a5ea0306107f4eec88aada9f6c6c75afdacb1bf762374"]
                            .into(),
                        hex!["e46ce812ed7c40e446f1a92a6be46856428ee9f38152c833991c00c4314649c6"]
                            .unchecked_into(),
                        hex!["c0fa3655fabf021d4358c1206a07885420e938ac288047258f3e33f7aebb770b"]
                            .unchecked_into(),
                        hex!["a84d71be232e639172a7263716d4d2502618005b3e8ac6ec21e7bfd5606ff016"]
                            .unchecked_into(),
                        hex!["0835dc13fbd5a581620a17a7517bd59e9d1ad63394b7e11d32b38df1a0bf742b"]
                            .unchecked_into(),
                    ),
                    (
                        // Boot Node/Validator 2: ip addres 94.130.184.125 (public keys in hex)
                        hex!["a6b1dcada564320266bba831f002f1e306d4919ea9ff4efe5ffcfa49304f5009"]
                            .into(),
                        hex!["70cf5306dcbbc988ea3d9a9ff0a19a22f123839233241636ebfbc7d15787b062"]
                            .into(),
                        hex!["4edf8af0a87ba1b06c9a1b2f77a1bf163cc2e0cfc54771125df4dd2b578ac1cb"]
                            .unchecked_into(),
                        hex!["12e7063e954499f1ebe9c09d42d34aac080e53a9ef8478ea6bdd44618d74d274"]
                            .unchecked_into(),
                        hex!["f254c663f6eff4be404f01c5a80c38210c08592d3f3c33771070fb2316d2aa12"]
                            .unchecked_into(),
                        hex!["d601e09399970bf8fd11fedd9fda45f60ee0d9f65a101f699021dbc132b95232"]
                            .unchecked_into(),
                    ),
                    (
                        // Boot Node/Validator 3: ip addres 94.130.183.49 (public keys in hex)
                        hex!["9a26fcf27e4157aee6a6e59fd1586d3e83288d5eedd5929968ebc21ccf93a547"]
                            .into(),
                        hex!["bc2763759855c9ca4bdc5e7b260036605462fd6ad1ffb0a5ea6ea2f8169d5464"]
                            .into(),
                        hex!["10dce40326ea7ee129dc7757515aa3695189df4ec34adda39fe51f636b49b41f"]
                            .unchecked_into(),
                        hex!["9e8c7741d6ff30c8f6e2637ca89a9a0503170f8cda39f4e763c4c9a3d3f43538"]
                            .unchecked_into(),
                        hex!["7ae5fc6382ba2c27a9719ca0e541d210312865db1cfafe48a860f92ff76c0247"]
                            .unchecked_into(),
                        hex!["1ef2ee8131b7279d0da66f5d7348e00acb29bcb7d01e80015164ab69408b4b69"]
                            .unchecked_into(),
                    ),
                ],
                // Sudo
                hex!["1457e343391f4e1c2644a378506d49e1ff1a59d6a854c0f99d20f9c4b74d383c"].into(),
                // Endowed accounts
                vec![
                    hex!["deeadc65c04777f95e8a6724da400834f3026bafb82f22fb8d3edc844d35ac6e"].into(),
                    hex!["12f3f0becb6d631913013a154b1f24ad474b12631959115ad66cf515904f762a"].into(),
                    hex!["70ca6312898f76dab454bd15074cd858b43448fea6e8881476e2c138305c151b"].into(),
                ],
            )
        },
        // Bootnodes
        vec![
            "/ip4/65.108.62.72/tcp/30333/p2p/12D3KooWPu79TFZHuZYU78mi72C1e8Dk37ot69Um8atNNiz9Hm2R"
                .parse()
                .unwrap(),
            "/ip4/94.130.184.125/tcp/30333/p2p/12D3KooWSZVBZtM1fetf2wCLSvRCLmYhisYFMJrqQn4eZdW1RFNi"
                .parse()
                .unwrap(),
            "/ip4/94.130.183.49/tcp/30333/p2p/12D3KooWSecRjwjJ6CFJLtCNacEzWBV2S46vrHD1DcC491fz13Ut"
                .parse()
                .unwrap(),
        ],
        // Telemetry
        TelemetryEndpoints::new(vec![(TELEMETRY_URL.into(), 0)]).ok(),
        // Protocol ID
        Some("aisland_testnet"),
        // Properties
        Some(aisland_properties()),
        // Extensions
        Default::default(),
    ))
}

pub fn mainnet_config() -> Result<ChainSpec, String> {
    let wasm_binary = WASM_BINARY.ok_or_else(|| "WASM binary not available".to_string())?;
    Ok(ChainSpec::from_genesis(
		// Name
		"Aisland Mainnet",
		// ID
		"aisland_mainnet",
		ChainType::Live,
		move || mainnet_genesis(
			wasm_binary,
			// Initial authorities keys:
			// stash
			// controller
			// grandpa
			// babe
			// im-online
			// authority-discovery
			vec![
				(   // boot node - validator 1
					hex!["b0737e722d5988f253eeb4d772a3f1177ae39cea6e5230ca9f36c6b58784dd0c"].into(),
					hex!["0af4f754f70707f465d7c9a4390176c7094262a83defae3f67dcf98428a35152"].into(),
					hex!["827f4f79c87bb5e1589c458e654928d377c7fe247b9698971f36b3886d077c73"].unchecked_into(),
					hex!["8a1d180e87eea7ad8f5a3a1c762e2b3a24a05f9fab0f2c2f9f1d3d2dd36f4638"].unchecked_into(),
					hex!["56bcf1a18384a3ba7a74324b00dfc237283ad4f726e90eac1e1f4691f1afb62f"].unchecked_into(),
					hex!["2aa508cc61fa7ea739adfcbe174731b154bd6ff4ebc51c45f8a1ef41f545dd64"].unchecked_into(),
				),
				(   // boot node - validator 2
					hex!["7c8b95a583a2ebc5281afce313a791febc52009a7b64da295cf26c4b033fd855"].into(),
					hex!["ee2cccba0d0fc5776c70a863b5bb4a8cf64127eb312ad5a190d1cc405d38fb71"].into(),
					hex!["0224a8f41eef0ddceb220993d5e9610b69b7aec3e1b60a9ad71a8a02a3e1b133"].unchecked_into(),
					hex!["5637617b04feb9933bc576678fc8a82e324cdbf823a9b334c5335ae8fa0d5d2d"].unchecked_into(),
					hex!["92294031a34926cba2f8cb07e9a0143531081ad150dd172af4ff3646a9fc2b75"].unchecked_into(),
					hex!["7c19e411a50412eea1040262190dd67e366a40f4c83236df279373702003665a"].unchecked_into(),
				),
				(   // boot node - validator 3
					hex!["82b07e9079d853f54dfc63564b3751fd4ee393fa59faa70fcabda06db6d67036"].into(),
					hex!["c058ec9085e737ea5162990d214174d2b552814fcb7eac407e5577cf65112236"].into(),
					hex!["0b34d6342c30d57690687b1d68aa44e08e405c0843673b3467c83985ad312293"].unchecked_into(),
					hex!["ecb522c88e895a58338210764b475ad23474835258db9ba80d8bd5beda63657c"].unchecked_into(),
					hex!["bee3de2cb6d6f5bb0cae3a8e4153acdf0180f5a682384f6a859cd62933991615"].unchecked_into(),
					hex!["c830456eccd9bb6e22545319ff9a3a772eec89d2020c1d2de5c4e26aff01956f"].unchecked_into(),
				),
                (   // boot node - validator 4
					hex!["f673ddbb4deb0d8b9bf4aa8ee1ce101d1a56bb6fd57011b71c4e9afbc438e270"].into(),
					hex!["ced0a8ea6374e004e4213b87e5029a1d5410fe8c18e2f8e262b3e8fa8ae03341"].into(),
					hex!["9f016f3dbc482fa93465a88c6c59b9242d024ef12b4e7e9bb3a8edce0a8a72ef"].unchecked_into(),
					hex!["46dd4d123ecd630d3853462f389b581fde141afd15de85d76e5781bdc262e501"].unchecked_into(),
					hex!["0e2c219d1aaf5ba61c14374e5441b66b12a46bb9ec9ea4c00b838928ec0c194f"].unchecked_into(),
					hex!["d4dee9a4744a42e5333a87e1f11e3b784fda81dab6a4438fd1a296bdffd58b27"].unchecked_into(),
				),
			],
			// Sudo
			hex!["86376ae63c12523faf04d8204aa88051018f77a8521abe41a21981d103a9f65e"].into(),
			// Endowed accounts
			vec![
				// 25 Initial Investors 
				(hex!["34327590b5e13f848fb5b5f595d88f346e0e660a0765c7814e6da819f476af39"].into(), 1_000_000 as u128),
                (hex!["ba3a96a7cc529f3cf4260c8c630f4fd96b905cd62cd8e2c6f6a73b848c141a20"].into(), 1_000_000 as u128),
                (hex!["f6c6b87b2a2c2bf8d4b4a2466276e8afe1b9071dfe54e4446d4a077f4361ef03"].into(), 1_000_000 as u128),
                (hex!["a635142b0441640118075a35c53f805e4fb9ff837df677f3172023d56da14c55"].into(), 1_000_000 as u128),
                (hex!["e4d00d108452c7d43e4ed6e8192af278a81e342a5887692a09b89cc0570bb429"].into(), 1_000_000 as u128),
                (hex!["26f67481478dbc8a2d506c7d701fbd343601a1af0e23428be9cc13247b772b12"].into(), 1_000_000 as u128),
                (hex!["5a2d58b6b1f0fd0a5465441d206a91c9b3681f3785d4715190b00139b4b68126"].into(), 1_000_000 as u128),
                (hex!["98a881ee93c155af4607d165801a987816c84e053033fad985a67a81d6d4fc78"].into(), 1_000_000 as u128),
                (hex!["e864895cce543b4a95a80cac03c72c81b2e4cb20d710779d8c71326522f05e1a"].into(), 1_000_000 as u128),
                (hex!["24614524bee1e9dddaa4001a9d9b44fb8ddbba0612cb72f7dccaa345ca6fe92d"].into(), 1_000_000 as u128),
                (hex!["5cdbc54a0695e743fd22548c18792c026bc4e494c8d51d15faa3b4d31fc61a67"].into(), 1_000_000 as u128),
                (hex!["f0cb2161c37a59f27a6511f4ed6667d92c52f7c5be5d73ccd0e6b8753f5d6a64"].into(), 1_000_000 as u128),
                (hex!["c8edbe53d229e822b107da22addc8ea8d036c4cfef1c4af7b960d92bbd4f3743"].into(), 1_000_000 as u128),
                (hex!["90fd007edb662dab1deee6eb671b72e3606b53e771e483c5e65a2ca89f559255"].into(), 1_000_000 as u128),
                (hex!["c23a89def4325818f9f0da193899c337b36b3929b8a48874a2f20623d5cd8f74"].into(), 1_000_000 as u128),
                (hex!["364ee2c88ea9659574e62ab5c0427f4f0dac860d12ebb896e2db062769438a7e"].into(), 1_000_000 as u128),
                (hex!["e26cf1fdcd473246b9faf6856c36d359c7c48321186c83ea41e066cfe9348c39"].into(), 1_000_000 as u128),
                (hex!["38948ee1091b8e3d97ed0f01ae0a3ea8d26a15b7ab7bf8ddc9ebb8103aa94d5a"].into(), 1_000_000 as u128),
                (hex!["32931c37b3dbac85db6803b6d668f866a3f9ad51ee83122f43168973e75ed246"].into(), 1_000_000 as u128),
                (hex!["8a55590ef7793a4afa0711a66993b211437c81148c7c9b645e7f469db34cd702"].into(), 1_000_000 as u128),
                (hex!["7a7beae22fe29ca3159648962f1e5fddc0ebbf7961ecc45b3dd48062286d5106"].into(), 1_000_000 as u128),
                (hex!["34f0843fd27b044090690d6a74e818a3763fc7a72a83b955dc2429025cfdc075"].into(), 1_000_000 as u128),
                (hex!["660024ab5f5619df42e565b8fe3b59baa0c30ac658e1dff1c19829fdf45d6a2d"].into(), 1_000_000 as u128),
                // Liquidity available for future investors
                (hex!["a4459efd92d4b57075912fe08491cb4e182abdcfc56f159b708c6fd00405ec3a"].into(), 73_000_000 as u128),
                // Sudo Account (super user)
                (hex!["86376ae63c12523faf04d8204aa88051018f77a8521abe41a21981d103a9f65e"].into(), 1_000_000 as u128),
				// Service account for gas-less transactions
				(hex!["3ab2bf92543aa64a59cb0b76a6608bba9be58698fd1d4732ac1eb5ea426fee77"].into(), 1_000_000 as u128),
			],
		),
		// Bootnodes
		vec![
			"/dns/validator1.aisland.io/tcp/30333/p2p/12D3KooWFHSc9cUcyNtavUkLg4VBAeBnYNgy713BnovUa9WNY5pp".parse().unwrap(),
			"/dns/validator2.aisland.io/tcp/30333/p2p/12D3KooWAQqcXvcvt4eVEgogpDLAdGWgR5bY1drew44We6FfJAYq".parse().unwrap(),
			"/dns/validator3.aisland.io/tcp/30333/p2p/12D3KooWCT7rnUmEK7anTp7svwr4GTs6k3XXnSjmgTcNvdzWzgWU".parse().unwrap(),
            "/dns/validator4.aisland.io/tcp/30333/p2p/12D3KooWCT7rnUmEK7anTp7svwr4GTs6k3XXnSjmgTcNvdzWzgWU".parse().unwrap(),
		],
		// Telemetry
		TelemetryEndpoints::new(vec![(TELEMETRY_URL.into(), 0)]).ok(),
		// Protocol ID
		Some("aisland_mainnet"),
		// Properties
		Some(aisland_properties()),
		// Extensions
		Default::default(),
	))
}

fn testnet_genesis(
    wasm_binary: &[u8],
    initial_authorities: Vec<(
        AccountId,
        AccountId,
        GrandpaId,
        BabeId,
        ImOnlineId,
        AuthorityDiscoveryId,
    )>,
    root_key: AccountId,
    endowed_accounts: Vec<AccountId>,
) -> GenesisConfig {
    let evm_genesis_accounts = evm_genesis();

    const INITIAL_BALANCE: u128 = 100_000_000 * AISC;
    const INITIAL_STAKING: u128 = 1_000_000 * AISC;
    let existential_deposit = MaxNativeTokenExistentialDeposit::get();
    let enable_println = true;
    let balances = initial_authorities
        .iter()
        .map(|x| (x.0.clone(), INITIAL_STAKING))
        .chain(
            endowed_accounts
                .iter()
                .cloned()
                .map(|k| (k, INITIAL_BALANCE)),
        )
        .chain(
            get_all_module_accounts()
                .iter()
                .map(|x| (x.clone(), existential_deposit)),
        )
        .fold(
            BTreeMap::<AccountId, Balance>::new(),
            |mut acc, (account_id, amount)| {
                if let Some(balance) = acc.get_mut(&account_id) {
                    *balance = balance
                        .checked_add(amount)
                        .expect("balance cannot overflow when building genesis");
                } else {
                    acc.insert(account_id.clone(), amount);
                }
                acc
            },
        )
        .into_iter()
        .collect::<Vec<(AccountId, Balance)>>();

    GenesisConfig {
        frame_system: Some(SystemConfig {
            // Add Wasm runtime to storage.
            code: wasm_binary.to_vec(),
            changes_trie_config: Default::default(),
        }),
        pallet_indices: Some(IndicesConfig { indices: vec![] }),
        pallet_balances: Some(BalancesConfig { balances }),
        pallet_session: Some(SessionConfig {
            keys: initial_authorities
                .iter()
                .map(|x| {
                    (
                        x.0.clone(), // stash
                        x.0.clone(), // stash
                        get_session_keys(
                            x.2.clone(), // grandpa
                            x.3.clone(), // babe
                            x.4.clone(), // im-online
                            x.5.clone(), // authority-discovery
                        ),
                    )
                })
                .collect::<Vec<_>>(),
        }),
        pallet_staking: Some(StakingConfig {
            validator_count: initial_authorities.len() as u32 * 2,
            minimum_validator_count: initial_authorities.len() as u32,
            stakers: initial_authorities
                .iter()
                .map(|x| {
                    (
                        x.0.clone(),
                        x.1.clone(),
                        INITIAL_STAKING,
                        StakerStatus::Validator,
                    )
                })
                .collect(),
            invulnerables: initial_authorities.iter().map(|x| x.0.clone()).collect(),
            slash_reward_fraction: sp_runtime::Perbill::from_percent(10),
            ..Default::default()
        }),
        pallet_babe: Some(BabeConfig {
            authorities: vec![],
        }),
        pallet_grandpa: Some(GrandpaConfig {
            authorities: vec![],
        }),
        pallet_authority_discovery: Some(AuthorityDiscoveryConfig { keys: vec![] }),
        pallet_im_online: Default::default(),
        orml_tokens: Some(TokensConfig {
            endowed_accounts: endowed_accounts
                .iter()
                .flat_map(|x| {
                    vec![(
                        x.clone(),
                        CurrencyId::Token(TokenSymbol::AISD),
                        INITIAL_BALANCE,
                    )]
                })
                .collect(),
        }),
        module_evm: Some(EvmConfig {
            accounts: evm_genesis_accounts,
        }),
        pallet_sudo: Some(SudoConfig { key: root_key }),
        pallet_collective_Instance1: Some(Default::default()),
        // Nft pallet
        orml_nft: Default::default(),
        // Smart contracts !Ink Language
        pallet_contracts: Some(ContractsConfig {
            current_schedule: pallet_contracts::Schedule {
                enable_println,
                ..Default::default()
            },
        }),
    }
}

fn mainnet_genesis(
    wasm_binary: &[u8],
    initial_authorities: Vec<(
        AccountId,
        AccountId,
        GrandpaId,
        BabeId,
        ImOnlineId,
        AuthorityDiscoveryId,
    )>,
    root_key: AccountId,
    endowed_accounts: Vec<(AccountId, Balance)>,
) -> GenesisConfig {
    let evm_genesis_accounts = evm_genesis();

    const INITIAL_STAKING: u128 = 1_000_000 * AISC;
    let existential_deposit = MaxNativeTokenExistentialDeposit::get();
    let enable_println = true;
    let balances = initial_authorities
        .iter()
        .map(|x| (x.0.clone(), INITIAL_STAKING * 2))
        .chain(
            endowed_accounts
                .iter()
                .cloned()
                .map(|x| (x.0.clone(), x.1 * AISC)),
        )
        .chain(
            get_all_module_accounts()
                .iter()
                .map(|x| (x.clone(), existential_deposit)),
        )
        .fold(
            BTreeMap::<AccountId, Balance>::new(),
            |mut acc, (account_id, amount)| {
                if let Some(balance) = acc.get_mut(&account_id) {
                    *balance = balance
                        .checked_add(amount)
                        .expect("balance cannot overflow when building genesis");
                } else {
                    acc.insert(account_id.clone(), amount);
                }
                acc
            },
        )
        .into_iter()
        .collect::<Vec<(AccountId, Balance)>>();

    GenesisConfig {
        frame_system: Some(SystemConfig {
            // Add Wasm runtime to storage.
            code: wasm_binary.to_vec(),
            changes_trie_config: Default::default(),
        }),
        pallet_indices: Some(IndicesConfig { indices: vec![] }),
        pallet_balances: Some(BalancesConfig { balances }),
        pallet_session: Some(SessionConfig {
            keys: initial_authorities
                .iter()
                .map(|x| {
                    (
                        x.0.clone(), // stash
                        x.0.clone(), // stash
                        get_session_keys(
                            x.2.clone(), // grandpa
                            x.3.clone(), // babe
                            x.4.clone(), // im-online
                            x.5.clone(), // authority-discovery
                        ),
                    )
                })
                .collect::<Vec<_>>(),
        }),
        pallet_staking: Some(StakingConfig {
            validator_count: initial_authorities.len() as u32 * 2,
            minimum_validator_count: initial_authorities.len() as u32,
            stakers: initial_authorities
                .iter()
                .map(|x| {
                    (
                        x.0.clone(),
                        x.1.clone(),
                        INITIAL_STAKING,
                        StakerStatus::Validator,
                    )
                })
                .collect(),
            invulnerables: initial_authorities.iter().map(|x| x.0.clone()).collect(),
            slash_reward_fraction: sp_runtime::Perbill::from_percent(10),
            ..Default::default()
        }),
        pallet_babe: Some(BabeConfig {
            authorities: vec![],
        }),
        pallet_grandpa: Some(GrandpaConfig {
            authorities: vec![],
        }),
        pallet_authority_discovery: Some(AuthorityDiscoveryConfig { keys: vec![] }),
        pallet_im_online: Default::default(),
        orml_tokens: Some(TokensConfig {
            endowed_accounts: vec![],
        }),
        module_evm: Some(EvmConfig {
            accounts: evm_genesis_accounts,
        }),
        pallet_sudo: Some(SudoConfig { key: root_key }),
        pallet_collective_Instance1: Some(Default::default()),
        // Nft pallet
        orml_nft: Default::default(),
        // Smart contracts !Ink Language
        pallet_contracts: Some(ContractsConfig {
            current_schedule: pallet_contracts::Schedule {
                enable_println,
                ..Default::default()
            },
        }),
    }
}

/// Token
pub fn aisland_properties() -> Properties {
    let mut p = Properties::new();
    p.insert("ss58format".into(), 42.into());
    p.insert("tokenDecimals".into(), 18.into());
    p.insert("tokenSymbol".into(), "AISC".into());
    p
}

/// Predeployed contract addresses
pub fn evm_genesis() -> BTreeMap<H160, module_evm::GenesisAccount<Balance, Nonce>> {
    let existential_deposit = MaxNativeTokenExistentialDeposit::get();
    let contracts_json = &include_bytes!("../../assets/bytecodes.json")[..];
    let contracts: Vec<(String, String, String)> = serde_json::from_slice(contracts_json).unwrap();
    let mut accounts = BTreeMap::new();
    for (_, address, code_string) in contracts {
        let account = module_evm::GenesisAccount {
            nonce: 0,
            balance: existential_deposit,
            storage: Default::default(),
            code: Bytes::from_str(&code_string).unwrap().0,
        };
        let addr = H160::from_slice(
            from_hex(address.as_str())
                .expect("predeploy-contracts must specify address")
                .as_slice(),
        );
        accounts.insert(addr, account);
    }
    accounts
}
