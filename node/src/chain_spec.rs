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
				(
					hex!["6c08c1f8e0cf1e200b24b43fca4c4e407b963b6b1e459d1aeff80c566a1da469"].into(),
					hex!["864eff3160ff8609c030316867630850a9d6e35c47d3efe54de44264fef7665e"].into(),
					hex!["dc41d9325da71d90806d727b826d125cd523da28eb39ab048ab983d7bb74fb32"].unchecked_into(),
					hex!["8a688a748fd39bedaa507c942600c40478c2082dee17b8263613fc3c086b0c53"].unchecked_into(),
					hex!["3a4e80c48718f72326b49c4ae80199d35285643751e75a743f30b7561b538676"].unchecked_into(),
					hex!["68d39d0d386ed4e9dd7e280d62e7dc9cf61dc508ef25efb74b6d740fa4dde463"].unchecked_into(),
				),
				(
					hex!["5c22097b5c8b5912ce28b72ba4de52c3da8aca9379c748c1356a6642107d4c4a"].into(),
					hex!["543fd4fd9a284c0f955bb083ae6e0fe7a584eb6f6e72b386071a250b94f99a59"].into(),
					hex!["f15a651be0ea0afcfe691a118ee7acfa114d11a27cf10991ee91ea97942d2135"].unchecked_into(),
					hex!["70e74bed02b733e47bc044da80418fd287bb2b7a0c032bd211d7956c68c9561b"].unchecked_into(),
					hex!["724cefffeaa10a44935a973511b9427a8c3c4fb08582afc4af8bf110fe4aac4b"].unchecked_into(),
					hex!["a068435c438ddc61b1b656e3f61c876e109706383cf4e27309cc1e308f88b86f"].unchecked_into(),
				),
				(
					hex!["a67f388c1b8d68287fb3288b5aa36f069875c15ebcb9b1e4e62678aad6b24b44"].into(),
					hex!["ec912201d98911842b1a8e82983f71f2116dd8b898798ece4e1d210590de7d60"].into(),
					hex!["347f5342875b9847ec089ca723c1c09cc532e53dca4b940a6138040025d94eb9"].unchecked_into(),
					hex!["64841d2d124e1b1dd5485a58908ab244b296b184ae645a0c103adcbcc565f070"].unchecked_into(),
					hex!["50a3452ca93800a8b660d624521c240e5cb20a47a33d23174bb7681811950646"].unchecked_into(),
					hex!["7a0caeb50fbcd657b8388adfaeca41a2ae3e85b8916a2ce92761ce1a4db89035"].unchecked_into(),
				),
			],
			// Sudo
			hex!["9c48c0498bdf1d716f4544fc21f050963409f2db8154ba21e5233001202cbf08"].into(),
			// Endowed accounts
			vec![
				// Investors
				(hex!["3c483acc759b79f8b12fa177e4bdfa0448a6ea03c389cf4db2b4325f0fc8f84a"].into(), 4_340_893_656 as u128),
				// Liquidity bridge reserves
				(hex!["5adebb35eb317412b58672db0434e4b112fcd27abaf28039f07c0db155b26650"].into(), 2_000_000_000 as u128),
				// Lockup & core nominators
				(hex!["746db342d3981b230804d1a187245e565f8eb3a2897f83d0d841cc52282e324c"].into(), 500_000_000 as u128),
				(hex!["da512d1335a62ad6f79baecfe87578c5d829113dc85dbb984d90a83f50680145"].into(), 500_000_000 as u128),
				(hex!["b493eacad9ca9d7d8dc21b940966b4db65dfbe01084f73c1eee2793b1b0a1504"].into(), 500_000_000 as u128),
				(hex!["849cf6f8a093c28fd0f699b47383767b0618f06aad9df61c4a9aff4af5809841"].into(), 250_000_000 as u128),
				(hex!["863bd6a38c7beb526be033068ac625536cd5d8a83cd51c1577a1779fab41655c"].into(), 250_000_000 as u128),
				(hex!["c2d2d7784e9272ef1785f92630dbce167a280149b22f2ae3b0262435e478884d"].into(), 250_000_000 as u128),
				// Sudo
				(hex!["9c48c0498bdf1d716f4544fc21f050963409f2db8154ba21e5233001202cbf08"].into(), 100_000_000 as u128),
				// Developer pool & faucet
				(hex!["1acc4a5c6361770eac4da9be1c37ac37ea91a55f57121c03240ceabf0b7c1c5e"].into(), 10_000_000 as u128),
			],
		),
		// Bootnodes
		vec![
			"/dns/bootnode-1.aisland.io/tcp/30333/p2p/12D3KooWFHSc9cUcyNtavUkLg4VBAeBnYNgy713BnovUa9WNY5pp".parse().unwrap(),
			"/dns/bootnode-2.aisland.io/tcp/30333/p2p/12D3KooWAQqcXvcvt4eVEgogpDLAdGWgR5bY1drew44We6FfJAYq".parse().unwrap(),
			"/dns/bootnode-3.aisland.io/tcp/30333/p2p/12D3KooWCT7rnUmEK7anTp7svwr4GTs6k3XXnSjmgTcNvdzWzgWU".parse().unwrap(),
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
